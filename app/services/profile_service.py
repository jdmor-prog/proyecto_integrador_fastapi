from sqlalchemy.orm import Session, selectinload
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate


def list_profiles(db: Session, skip: int = 0, limit: int = 100, user_id: int | None = None) -> list[Profile]:
    q = db.query(Profile).options(selectinload(Profile.user))
    if user_id is not None:
        q = q.filter(Profile.user_id == user_id)
    return q.order_by(Profile.id.asc()).offset(skip).limit(limit).all()


def get_profile(db: Session, profile_id: int) -> Profile | None:
    return db.query(Profile).options(selectinload(Profile.user)).filter(Profile.id == profile_id).first()


def get_profile_by_user_id(db: Session, user_id: int) -> Profile | None:
    return db.query(Profile).options(selectinload(Profile.user)).filter(Profile.user_id == user_id).first()


def create_profile(db: Session, payload: ProfileCreate) -> Profile:
    # Validar que el usuario exista
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise ValueError("Usuario no encontrado")
    # Un perfil por usuario
    existing = get_profile_by_user_id(db, payload.user_id)
    if existing:
        raise ValueError("El usuario ya tiene un perfil")

    profile = Profile(
        user_id=payload.user_id,
        bio=payload.bio,
        phone=payload.phone,
        avatar_url=payload.avatar_url,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, profile_id: int, payload: ProfileUpdate) -> Profile | None:
    profile = get_profile(db, profile_id)
    if not profile:
        return None
    if payload.user_id is not None and payload.user_id != profile.user_id:
        # Permitir reasignar perfil a otro usuario solo si ese otro no tiene perfil
        if not db.query(User).filter(User.id == payload.user_id).first():
            raise ValueError("Usuario no encontrado")
        if get_profile_by_user_id(db, payload.user_id):
            raise ValueError("El usuario de destino ya tiene un perfil")
        profile.user_id = payload.user_id
    if payload.bio is not None:
        profile.bio = payload.bio
    if payload.phone is not None:
        profile.phone = payload.phone
    if payload.avatar_url is not None:
        profile.avatar_url = payload.avatar_url
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def delete_profile(db: Session, profile_id: int) -> bool:
    profile = get_profile(db, profile_id)
    if not profile:
        return False
    db.delete(profile)
    db.commit()
    return True