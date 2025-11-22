from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user

def admin_required(current_user = Depends(get_current_active_user)):
    # current_user must have attribute 'rol'
    if not current_user or getattr(current_user, "rol", "").upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions (admin required)."
        )
    return current_user
