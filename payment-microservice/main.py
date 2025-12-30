from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
import random
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from metrics import (
    payments_total,
    payments_success,
    payments_failed,
    payment_amount,
    payment_latency,                        
    http_requests_total, 
    http_request_latency_seconds
)

app = FastAPI(title="Payment Service")

# -----------------------------
# Middleware
# -----------------------------
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    http_requests_total.labels(
        request.method,
        request.url.path,
        response.status_code
    ).inc()

    http_request_latency_seconds.labels(
        request.url.path
    ).observe(duration)

    return response


# -----------------------------
# Models
# -----------------------------
class PaymentRequest(BaseModel):
    user_id: str = Field(..., example="1ee45954-1461-475c-a0da-aee69b3ddbf2")
    amount: float = Field(..., gt=0, example=120.50)


class PaymentResponse(BaseModel):
    status: str
    amount: float


# -----------------------------
# Health
# -----------------------------
@app.get("/api/payments/health")
def health():
    return {"status": "payment ok"}


# -----------------------------
# Pay
# -----------------------------
@app.post("/api/payments/pay")
def pay(data: PaymentRequest):
    payments_total.inc()

    time.sleep(random.uniform(0.05, 0.3))
    success = random.random() > 0.2

    if success:
        payments_success.inc()
        payment_amount.inc(data.amount)
        return {"status": "success", "amount": data.amount}

    payments_failed.inc()
    return {"status": "failed", "amount": data.amount}


# -----------------------------
# Refund
# -----------------------------
@app.post("/api/payments/refund")
def refund(data: PaymentRequest):
    payments_failed.inc()
    payment_amount.inc(-data.amount)
    return {"status": "refunded", "amount": data.amount}


# -----------------------------
# Metrics
# -----------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
