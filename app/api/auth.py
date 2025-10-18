from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class Login(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register_user(p: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == p.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(email=p.email, full_name=p.full_name, hashed_password=hash_password(p.password))
    db.add(u); db.commit(); db.refresh(u)
    return {"msg": "User registered successfully", "email": u.email}

@router.post("/login")
def login_user(p: Login, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == p.email).first()
    if not u or not verify_password(p.password, u.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(sub=u.email, expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "token_type": "bearer"}

def _current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        email = decode_token(creds.credentials).get("sub")
        if not email:
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    u = db.query(User).filter(User.email == email).first()
    if not u:
        raise HTTPException(status_code=401, detail="User not found")
    return u

@router.get("/me")
def me(user: User = Depends(_current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name}
