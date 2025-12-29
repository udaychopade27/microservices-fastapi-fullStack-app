from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import Order, OrderItem
from pydantic import BaseModel
import requests
import os
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service")

INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory:8001")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://payment:8003")


class CheckoutItem(BaseModel):
    product_id: int
    qty: int


class CheckoutRequest(BaseModel):
    user_id: str
    items: list[CheckoutItem]

@app.post("/orders/checkout")
def checkout(data: CheckoutRequest, db: Session = Depends(get_db)):

    # -------------------------------
    # STEP 1 — Load products & validate
    # -------------------------------
    try:
        products = requests.get(f"{INVENTORY_URL}/products", timeout=5).json()
    except:
        raise HTTPException(502, "Inventory service unavailable")

    product_map = {p["id"]: p for p in products}

    total = 0
    for i in data.items:
        product = product_map.get(i.product_id)
        if not product:
            raise HTTPException(404, f"Product {i.product_id} not found")

        total += product["price"] * i.qty

    # -------------------------------
    # STEP 2 — Reserve Inventory
    # -------------------------------
    reserved_items = []

    for i in data.items:
        try:
            r = requests.post(
                f"{INVENTORY_URL}/reserve/{i.product_id}",
                params={"qty": i.qty},
                timeout=5
            ).json()
        except:
            raise HTTPException(502, "Inventory service unavailable")

        if r.get("status") != "reserved":
            # rollback anything already reserved
            for x in reserved_items:
                requests.post(
                    f"{INVENTORY_URL}/release/{x.product_id}",
                    params={"qty": x.qty}
                )

            raise HTTPException(400, f"Product {i.product_id} out of stock")

        reserved_items.append(i)

    # -------------------------------
    # STEP 3 — Call Payment
    # -------------------------------
    try:
        pay = requests.post(
            f"{PAYMENT_URL}/pay",
            json={
                "user_id": data.user_id,
                "amount": total
            },
            timeout=5
        ).json()
    except:
        # Payment service down → rollback inventory
        for i in reserved_items:
            requests.post(
                f"{INVENTORY_URL}/release/{i.product_id}",
                params={"qty": i.qty}
            )

        raise HTTPException(502, "Payment service unavailable")

    payment_status = pay.get("status", "failed")
    status = "PAID" if payment_status == "success" else "FAILED"

    # -------------------------------
    # STEP 4 — Create Order
    # -------------------------------
    order = Order(
        user_id=data.user_id,
        total=total,
        status=status,
        created_at=datetime.utcnow()
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # -------------------------------
    # STEP 5 — If payment failed → release inventory
    # -------------------------------
    if status == "FAILED":
        for i in reserved_items:
            requests.post(
                f"{INVENTORY_URL}/release/{i.product_id}",
                params={"qty": i.qty}
            )

        return {
            "order_id": order.id,
            "status": "FAILED",
            "total": total
        }

    # -------------------------------
    # STEP 6 — Save Order Items
    # -------------------------------
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

    return {
        "order_id": order.id,
        "status": "PAID",
        "total": total
    }

    
@app.get("/orders/all")
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()



@app.get("/orders/{user_id}")
def get_orders(user_id: str, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == user_id).all()


@app.get("/orders/by-id/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(404)

    return {
        "id": o.id,
        "user_id": o.user_id,
        "status": o.status,
        "total": o.total,
        "created_at": o.created_at,
        "items": [
            {
                "product_id": i.product_id,
                "qty": i.qty,
                "price": i.price,
                "line_total": i.line_total
            } for i in o.items
        ]
    }


@app.get("/health")
def health():       
    return {"status": "order ok"}   