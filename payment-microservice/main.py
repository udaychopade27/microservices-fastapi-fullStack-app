from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import random

app = FastAPI(title="Payment Service")


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
# Health Check
# -----------------------------

@app.get("/health")
def health():
    return {"status": "payment ok"}


# -----------------------------
# Payment
# -----------------------------

@app.post("/pay", response_model=PaymentResponse)
def pay(data: PaymentRequest):
    """
    Simulated payment processor.
    Always returns:
    {
      status: "success" | "failed",
      amount: number
    }
    """

    # 80% success rate
    success = random.random() > 0.2

    if success:
        return {
            "status": "success",
            "amount": data.amount
        }

    return {
        "status": "failed",
        "amount": data.amount
    }


# -----------------------------
# Refund
# -----------------------------

@app.post("/refund", response_model=PaymentResponse)
def refund(data: PaymentRequest):
    """
    Refund always succeeds.
    """
    return {
        "status": "refunded",
        "amount": data.amount
    }
