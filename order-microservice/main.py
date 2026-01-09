from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import Order, OrderItem
from pydantic import BaseModel
import requests, os, time
from datetime import datetime
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from metrics import (
    http_requests_total,
    http_request_latency,
    orders_created,
    orders_paid,
    orders_failed,
    revenue_total,
    refund_total,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service")

INVENTORY_URL = os.getenv("INVENTORY_URL")
PAYMENT_URL = os.getenv("PAYMENT_URL")

# --------------------------------------------------
# Schemas
# --------------------------------------------------

class CheckoutItem(BaseModel):
    product_id: int
    qty: int

class CheckoutRequest(BaseModel):
    user_id: str
    items: list[CheckoutItem]

class RefundItem(BaseModel):
    product_id: int
    qty: int

class RefundRequest(BaseModel):
    items: list[RefundItem] | None = None
    
def get_current_user(request: Request):
    user_id = request.headers.get("x-user-id")
    role = request.headers.get("x-user-role")

    if not user_id or not role:
        raise HTTPException(401, "Unauthorized")

    return {
        "user_id": user_id,
        "role": role
    }

# --------------------------------------------------
# Middleware (Prometheus)
# --------------------------------------------------

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    path = "/api/orders/*" if request.url.path.startswith("/api/orders/") else request.url.path

    http_requests_total.labels(
        request.method,
        path,
        str(response.status_code)
    ).inc()

    http_request_latency.labels(path).observe(duration)
    return response

# --------------------------------------------------
# Health & Metrics
# --------------------------------------------------

@app.get("/api/orders/health")
def health():
    return {"status": "order ok"}

@app.get("/api/orders/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

# --------------------------------------------------
# Checkout (Saga)
# --------------------------------------------------

@app.post("/api/orders/checkout")
def checkout(data: CheckoutRequest, db: Session = Depends(get_db)):

    try:
        products = requests.get(
            f"{INVENTORY_URL}/api/inventory/products",
            timeout=5
        ).json()
    except:
        raise HTTPException(502, "Inventory service unavailable")

    product_map = {int(p["id"]): p for p in products if isinstance(p, dict)}

    total = 0
    for i in data.items:
        if i.product_id not in product_map:
            raise HTTPException(404, f"Product {i.product_id} not found")
        total += product_map[i.product_id]["price"] * i.qty

    order = Order(
        user_id=data.user_id,
        total=total,
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    reserved_items: list[CheckoutItem] = []

    try:
        # 1️⃣ Reserve inventory
        for i in data.items:
            r = requests.post(
                f"{INVENTORY_URL}/api/inventory/reserve/{i.product_id}",
                params={"qty": i.qty},
                timeout=5
            ).json()

            if r.get("status") != "reserved":
                raise Exception("Inventory reservation failed")

            reserved_items.append(i)

        # 2️⃣ Payment
        pay = requests.post(
            f"{PAYMENT_URL}/api/payments/pay",
            json={
                "user_id": data.user_id,
                "order_id": order.id,
                "amount": total
            },
            timeout=5
        ).json()

        orders_created.inc()

        if pay.get("status") != "success":
            raise Exception("Payment failed")

        # 3️⃣ Finalize order
        order.status = "PAID"
        orders_paid.inc()
        revenue_total.inc(total)

        for i in data.items:
            p = product_map[i.product_id]
            db.add(OrderItem(
                order_id=order.id,
                product_id=i.product_id,
                qty=i.qty,
                price=p["price"],
                line_total=p["price"] * i.qty
            ))

        db.commit()

        return {
            "order_id": order.id,
            "status": "PAID",
            "total": total
        }

    except Exception:
        orders_failed.inc()

        # Rollback inventory
        for i in reserved_items:
            requests.post(
                f"{INVENTORY_URL}/api/inventory/release/{i.product_id}",
                params={"qty": i.qty},
                timeout=5
            )

        order.status = "FAILED"
        db.commit()
        raise HTTPException(400, "Checkout failed")

# --------------------------------------------------
# Refund (Full + Partial)
# --------------------------------------------------

@app.post("/api/orders/refund/{order_id}")
def refund(
    order_id: int,
    data: RefundRequest | None = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    # -----------------------
    # AUTHORIZATION
    # -----------------------
    user = get_current_user(request)

    if user["role"] == "OWNER":
        raise HTTPException(403, "Owners cannot initiate refunds")

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.user_id != user["user_id"]:
        raise HTTPException(403, "You can only refund your own orders")

    if order.status != "PAID":
        raise HTTPException(400, "Order not refundable")

    refund_items: list[tuple[int, int]] = []
    refund_amount = 0.0

    # -----------------------
    # FULL REFUND
    # -----------------------
    if not data or not data.items:
        for item in order.items:
            refund_items.append((item.product_id, item.qty))
            refund_amount += item.line_total
            db.delete(item)

        order.total = 0
        order.status = "REFUNDED"

    # -----------------------
    # PARTIAL REFUND
    # -----------------------
    else:
        item_map = {i.product_id: i for i in order.items}

        for r in data.items:
            if r.product_id not in item_map:
                raise HTTPException(400, f"Invalid product {r.product_id}")

            oi = item_map[r.product_id]

            if r.qty <= 0 or r.qty > oi.qty:
                raise HTTPException(400, "Invalid refund quantity")

            refund_line = oi.price * r.qty
            refund_amount += refund_line
            refund_items.append((oi.product_id, r.qty))

            oi.qty -= r.qty
            oi.line_total -= refund_line

            if oi.qty == 0:
                db.delete(oi)

        order.total -= refund_amount
        order.status = "PARTIALLY_REFUNDED"

    # -----------------------
    # PAYMENT REFUND
    # -----------------------
    requests.post(
        f"{PAYMENT_URL}/api/payments/refund",
        json={
            "user_id": order.user_id,
            "order_id": order.id,
            "amount": refund_amount
        },
        timeout=5
    )

    # -----------------------
    # INVENTORY RESTORE
    # -----------------------
    for pid, qty in refund_items:
        requests.post(
            f"{INVENTORY_URL}/api/inventory/release/{pid}",
            params={"qty": qty},
            timeout=5
        )

    # -----------------------
    # METRICS (FIXED)
    # -----------------------
    # Counters can ONLY increase
    refund_total.inc(refund_amount)

    db.commit()

    return {
        "order_id": order.id,
        "refunded_amount": refund_amount,
        "status": order.status
    }

# --------------------------------------------------
# Queries
# --------------------------------------------------

@app.get("/api/orders/all")
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@app.get("/api/orders/{user_id}")
def get_orders(user_id: str, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == user_id).all()

@app.get("/api/orders/by-id/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(404)

    products = requests.get(
        f"{INVENTORY_URL}/api/inventory/products",
        timeout=5
    ).json()

    name_map = {int(p["id"]): p["name"] for p in products if isinstance(p, dict)}

    return {
        "id": o.id,
        "user_id": o.user_id,
        "status": o.status,
        "total": o.total,
        "created_at": o.created_at,
        "items": [
            {
                "product_id": i.product_id,
                "product_name": name_map.get(i.product_id, f"Product {i.product_id}"),
                "qty": i.qty,
                "price": i.price,
                "line_total": i.line_total
            }
            for i in o.items
        ]
    }
