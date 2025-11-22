from fastapi import Depends, HTTPException, Request, status

def admin_required(request: Request):
    user = request.state.user
    if not user or user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores"
        )
