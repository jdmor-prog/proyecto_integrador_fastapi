from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt  # PyJWT
from fastapi import HTTPException, status
from app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_minutes: int | None = None) -> str:
    """Create a JWT token with HS256 and expiration.
    Payload must include user identifiers and role.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token; raises HTTPException if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")