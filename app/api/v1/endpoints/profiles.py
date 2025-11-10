from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session
from app.schemas.profile import ProfileRead, ProfileCreate, ProfileUpdate, ProfileReadWithUser
from app.core.database import get_db
from app.services import profile_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileReadWithUser)
def get_my_profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Autorización requerida")
    prof = profile_service.get_profile_by_user_id(db, int(user_id))
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil no encontrado para el usuario")
    return prof

@router.get("/", response_model=list[ProfileReadWithUser])
def list_profiles(skip: int = 0, limit: int = 100, user_id: int | None = None, db: Session = Depends(get_db)):
    profiles = profile_service.list_profiles(db, skip=skip, limit=limit, user_id=user_id)
    return profiles


@router.post("/", response_model=ProfileReadWithUser)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    try:
        new_profile = profile_service.create_profile(db, payload)
        return new_profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{profile_id}", response_model=ProfileReadWithUser)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    prof = profile_service.get_profile(db, profile_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return prof


@router.put("/{profile_id}", response_model=ProfileReadWithUser)
def update_profile(profile_id: int, payload: ProfileUpdate, db: Session = Depends(get_db)):
    try:
        prof = profile_service.update_profile(db, profile_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return prof


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    ok = profile_service.delete_profile(db, profile_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)