from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import get_user_by_email
from app.core.security import create_access_token
import bcrypt
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from app.core.config import settings

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    # Accept either email or username via alias "email" for backward compatibility
    identifier: str = Field(alias="email")
    password: str
    model_config = ConfigDict(populate_by_name=True)


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Basic login that returns a JWT if credentials are valid."""
    ident = payload.identifier.strip()
    # Decide lookup strategy: email if contains '@', else by username (name)
    if "@" in ident:
        user = get_user_by_email(db, ident)
    else:
        from app.services.user_service import get_user_by_name
        user = get_user_by_name(db, ident)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not bcrypt.checkpw(payload.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    # Set JWT in HttpOnly cookie for browser-based docs/clients
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.jwt_expiration_minutes * 60,
        secure=False,  # set True in production over HTTPS
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile")
def profile(request: Request):
    """Return current user claims from JWT."""
    return {"user_id": request.state.user_id, "email": request.state.email, "role": request.state.role}


@router.get("/admin")
def admin_area():
    """Simple admin-only endpoint."""
    return {"message": "Área de administración"}


@router.post("/logout")
def logout(response: Response):
    """Clear JWT cookie to logout browser-based sessions."""
    response.delete_cookie("access_token")
    return {"message": "Logged out"}