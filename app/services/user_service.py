from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
import bcrypt


def list_users(db: Session, skip: int = 0, limit: int = 100, search: str | None = None) -> list[User]:
    q = db.query(User).options(selectinload(User.items), selectinload(User.profile))
    if search:
        like = f"%{search}%"
        q = q.filter(or_(User.name.like(like), User.email.like(like)))
    return q.order_by(User.id.asc()).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).options(selectinload(User.items), selectinload(User.profile)).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_name(db: Session, name: str) -> User | None:
    return db.query(User).filter(User.name == name).first()


def create_user(db: Session, payload: UserCreate) -> User:
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise ValueError("Email ya registrado")
    # Hash password using bcrypt
    hashed = bcrypt.hashpw(payload.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(name=payload.name, email=payload.email, hashed_password=hashed, role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User | None:
    user = get_user(db, user_id)
    if not user:
        return None
    if payload.email and payload.email != user.email:
        if get_user_by_email(db, payload.email):
            raise ValueError("Email ya registrado")
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    if payload.password is not None:
        user.hashed_password = bcrypt.hashpw(payload.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    if payload.role is not None:
        user.role = payload.role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True