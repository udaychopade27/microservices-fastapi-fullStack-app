from typing import Dict
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import Order, OrderItem
from pydantic import BaseModel
import requests
import os
from datetime import datetime
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics import (
    http_requests_total,
    http_request_latency,
    orders_created,
    orders_paid,
    orders_failed,
    order_amount
)
import time

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service")

INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory:8001")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://payment:8003")

# ----------------------------------------
# Models
# ----------------------------------------

class CheckoutItem(BaseModel):
    product_id: int
    qty: int

class CheckoutRequest(BaseModel):
    user_id: str
    items: list[CheckoutItem]

# ----------------------------------------
# Prometheus Middleware (SRE Safe)
# ----------------------------------------

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    path = request.url.path
    if path.startswith("/api/orders/"):
        path = "/api/orders/{id}"

    http_requests_total.labels(
        request.method,
        path,
        str(response.status_code)
    ).inc()

    http_request_latency.labels(path).observe(duration)

    return response

# ----------------------------------------
# Checkout
# ----------------------------------------

@app.post("/api/orders/checkout")
def checkout(data: CheckoutRequest, db: Session = Depends(get_db)):

    # Step 1 — Load Products
    try:
        products = requests.get(f"{INVENTORY_URL}/api/inventory/products", timeout=5).json()
    except:
        raise HTTPException(502, "Inventory service unavailable")

    product_map = {int(p["id"]): p for p in products if isinstance(p, dict)}

    total = 0
    for i in data.items:
        product = product_map.get(i.product_id)
        if not product:
            raise HTTPException(404, f"Product {i.product_id} not found")
        total += product["price"] * i.qty

    # Step 2 — Reserve Inventory
    reserved_items = []

    for i in data.items:
        try:
            r = requests.post(
                f"{INVENTORY_URL}/api/inventory/reserve/{i.product_id}",
                params={"qty": i.qty},
                timeout=5
            ).json()
        except:
            raise HTTPException(502, "Inventory service unavailable")

        if r.get("status") != "reserved":
            for x in reserved_items:
                requests.post(
                    f"{INVENTORY_URL}/api/inventory/release/{x.product_id}",
                    params={"qty": x.qty}
                )
            raise HTTPException(400, f"Product {i.product_id} out of stock")

        reserved_items.append(i)

    # Step 3 — Call Payment
    try:
        pay = requests.post(
            f"{PAYMENT_URL}/api/payments/pay",
            json={"user_id": data.user_id, "amount": total},
            timeout=5
        ).json()
    except:
        for i in reserved_items:
            requests.post(
                f"{INVENTORY_URL}/api/inventory/release/{i.product_id}",
                params={"qty": i.qty}
            )
        raise HTTPException(502, "Payment service unavailable")

    payment_status = pay.get("status", "failed")
    status = "PAID" if payment_status == "success" else "FAILED"

    # Step 3.5 — Business Metrics
    orders_created.inc()
    if status == "PAID":
        orders_paid.inc()
        order_amount.inc(total)
    else:
        orders_failed.inc()

    # Step 4 — Create Order
    order = Order(
        user_id=data.user_id,
        total=total,
        status=status,
        created_at=datetime.utcnow()
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # Step 5 — Release if failed
    if status == "FAILED":
        for i in reserved_items:
            requests.post(
                f"{INVENTORY_URL}/api/inventory/release/{i.product_id}",
                params={"qty": i.qty}
            )

        return {"order_id": order.id, "status": "FAILED", "total": total}

    # Step 6 — Save Order Items
    for i in data.items:
        product = product_map[i.product_id]
        price = product["price"]

        db.add(OrderItem(
            order_id=order.id,
            product_id=i.product_id,
            qty=i.qty,
            price=price,
            line_total=price * i.qty
        ))

    db.commit()

    return {"order_id": order.id, "status": "PAID", "total": total}

# ----------------------------------------
# Queries
# ----------------------------------------

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

    product_map = {}
    try:
        products = requests.get(f"{INVENTORY_URL}/api/inventory/products", timeout=5).json()
        for p in products:
            if isinstance(p, dict):
                product_map[int(p["id"])] = p["name"]
    except:
        pass

    return {
        "id": o.id,
        "user_id": o.user_id,
        "status": o.status,
        "total": o.total,
        "created_at": o.created_at,
        "items": [
            {
                "product_id": i.product_id,
                "product_name": product_map.get(i.product_id, f"Product #{i.product_id}"),
                "qty": i.qty,
                "price": i.price,
                "line_total": i.line_total
            }
            for i in o.items
        ]
    }

# ----------------------------------------
# Health & Metrics
# ----------------------------------------

@app.get("/api/orders/health")
def health():
    return {"status": "order ok"}

@app.get("/api/orders/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
