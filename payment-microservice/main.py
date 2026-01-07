from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import random
import time

from db import Base, engine, get_db
from models import Payment

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics import (
    payments_total,
    payments_success,
    payments_failed,
    payment_amount,
    payment_latency,
    http_requests_total,
    http_request_latency_seconds
)

# -------------------------------------------------
# App & DB Init
# -------------------------------------------------

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Service")

# -------------------------------------------------
# Middleware (HTTP Metrics)
# -------------------------------------------------

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    http_requests_total.labels(
        request.method,
        request.url.path,
        str(response.status_code)
    ).inc()

    http_request_latency_seconds.labels(
        request.url.path
    ).observe(duration)

    return response

# -------------------------------------------------
# Models
# -------------------------------------------------

class PaymentRequest(BaseModel):
    user_id: str = Field(..., example="1ee45954-1461-475c-a0da-aee69b3ddbf2")
    order_id: int = Field(..., example=101)
    amount: float = Field(..., gt=0, example=120.50)

class PaymentResponse(BaseModel):
    status: str
    amount: float

# -------------------------------------------------
# Health
# -------------------------------------------------

@app.get("/api/payments/health")
def health():
    return {"status": "payment ok"}

# -------------------------------------------------
# Pay
# -------------------------------------------------

@app.post("/api/payments/pay", response_model=PaymentResponse)
def pay(data: PaymentRequest, db: Session = Depends(get_db)):
    payments_total.inc()

    start = time.time()
    time.sleep(random.uniform(0.05, 0.3))  # simulate gateway latency
    success = random.random() > 0.2
    latency = time.time() - start

    payment_latency.observe(latency)

    if success:
        status = "SUCCESS"
        payments_success.inc()
        payment_amount.inc(data.amount)
    else:
        status = "FAILED"
        payments_failed.inc()

    # Persist payment
    payment = Payment(
        order_id=data.order_id,
        user_id=data.user_id,
        amount=data.amount,
        status=status,
        gateway_latency=latency
    )

    db.add(payment)
    db.commit()

    return {
        "status": status.lower(),
        "amount": data.amount
    }

# -------------------------------------------------
# Refund
# -------------------------------------------------

@app.post("/api/payments/refund", response_model=PaymentResponse)
def refund(data: PaymentRequest, db: Session = Depends(get_db)):
    payments_failed.inc()
    payment_amount.inc(-data.amount)

    refund_tx = Payment(
        order_id=data.order_id,
        user_id=data.user_id,
        amount=-data.amount,
        status="REFUNDED",
        gateway_latency=0
    )

    db.add(refund_tx)
    db.commit()

    return {
        "status": "refunded",
        "amount": data.amount
    }

# -------------------------------------------------
# Metrics
# -------------------------------------------------

@app.get("/api/payments/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
