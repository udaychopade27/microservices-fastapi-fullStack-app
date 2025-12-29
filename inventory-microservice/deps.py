from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
import os

security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET")

def get_current_user(token=Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def owner_required(user=Depends(get_current_user)):
    if user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Owner only")
    return user
