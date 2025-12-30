from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import User
from auth import hash_password, verify_password, create_access_token
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

from metrics import (
    auth_requests,
    auth_latency,
    auth_login_attempts,
    auth_login_success,
    auth_login_failed,
    auth_signup,
    http_requests_total, 
    http_request_latency_seconds
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

# ===============================
# MODELS
# ===============================
class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str   # OWNER or CLIENT

class LoginRequest(BaseModel):
    username: str
    password: str


# ===============================
# PROMETHEUS MIDDLEWARE
# ===============================
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


# ===============================
# REGISTER
# ===============================
@app.post("/api/auth/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.role not in ["OWNER", "CLIENT"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Metrics
    auth_signup.inc()

    return {
        "id": user.id,
        "message": "User registered"
    }


# ===============================
# LOGIN
# ===============================
@app.post("/api/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    auth_login_attempts.inc()

    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        auth_login_failed.inc()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    auth_login_success.inc()

    token = create_access_token(str(user.id), user.role)

    return {
        "access_token": token,
        "role": user.role,
        "user_id": user.id
    }


# ===============================
# METRICS
# ===============================
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ===============================
# HEALTH
# ===============================
@app.get("/api/auth/health")
def health():
    return {"status": "auth ok"}
