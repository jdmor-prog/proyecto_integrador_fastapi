from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.schemas.user import UserReadFull, UserCreate, UserUpdate
from app.core.database import get_db
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserReadFull])
def list_users(skip: int = 0, limit: int = 100, search: str | None = None, db: Session = Depends(get_db)):
    users = user_service.list_users(db, skip=skip, limit=limit, search=search)
    return users


@router.post("/", response_model=UserReadFull)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = user_service.create_user(db, user)
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserReadFull)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.put("/{user_id}", response_model=UserReadFull)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = user_service.update_user(db, user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Actualización puntual con PATCH (parcial)
@router.patch("/{user_id}", response_model=UserReadFull)
def patch_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = user_service.update_user(db, user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    ok = user_service.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)