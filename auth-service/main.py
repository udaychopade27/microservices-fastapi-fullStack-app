from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import User
from auth import hash_password, verify_password, create_access_token
from pydantic import BaseModel

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str   # OWNER or CLIENT

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
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

    return {"id": user.id, "message": "User registered"}

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user.id), user.role)

    return {
        "access_token": token,
        "role": user.role,
        "user_id": user.id
    }

@app.get("/health")
def health():
    return {"status": "auth ok"}
