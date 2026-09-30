import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db
from . import models

SECRET = os.getenv("SECRET_KEY", "dev-secret")
ALGO = "HS256"
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(p): return pwd.hash(p)
def verify_password(p, h): return pwd.verify(p, h)

def create_token(user_id: int):
    exp = datetime.utcnow() + timedelta(hours=12)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET, algorithm=ALGO)

def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    try:
        uid = int(jwt.decode(token, SECRET, algorithms=[ALGO])["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(models.User, uid)
    if not user:
        raise HTTPException(401, "User not found")
    return user
