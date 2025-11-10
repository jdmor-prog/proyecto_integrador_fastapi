from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session, skip: int = 0, limit: int = 100, q: str | None = None) -> list[Category]:
    qy = db.query(Category).options(selectinload(Category.items))
    if q:
        like = f"%{q}%"
        qy = qy.filter(or_(Category.name.like(like), Category.description.like(like)))
    return qy.order_by(Category.id.asc()).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: int) -> Category | None:
    return db.query(Category).options(selectinload(Category.items)).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Category | None:
    return db.query(Category).filter(Category.name == name).first()


def create_category(db: Session, payload: CategoryCreate) -> Category:
    if get_category_by_name(db, payload.name):
        raise ValueError("La categoría ya existe")
    cat = Category(name=payload.name, description=payload.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Category | None:
    cat = get_category(db, category_id)
    if not cat:
        return None
    if payload.name is not None:
        # Evitar duplicados de nombre
        exists = db.query(Category).filter(Category.name == payload.name, Category.id != category_id).first()
        if exists:
            raise ValueError("Otra categoría ya usa ese nombre")
        cat.name = payload.name
    if payload.description is not None:
        cat.description = payload.description
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def delete_category(db: Session, category_id: int) -> bool:
    cat = get_category(db, category_id)
    if not cat:
        return False
    db.delete(cat)
    db.commit()
    return True