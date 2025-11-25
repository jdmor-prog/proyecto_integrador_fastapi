from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models import User, UserRole
from app.schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserPasswordResetRequest,
    UserPasswordReset,
    UserOut,
)

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=UserRole.user,
        phone=payload.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role.value})
    return TokenResponse(access_token=token)


@router.post("/forgot-password")
def forgot_password(payload: UserPasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = create_access_token({"sub": user.id, "action": "reset"}, expires_minutes=30)
    user.reset_token = token
    user.reset_token_expires_at = expires_at
    db.commit()
    return {"reset_token": token, "expires_at": expires_at}


@router.post("/reset-password")
def reset_password(payload: UserPasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    if not user or not user.reset_token_expires_at or user.reset_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    user.hashed_password = get_password_hash(payload.new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()
    return {"detail": "Contraseña actualizada"}
