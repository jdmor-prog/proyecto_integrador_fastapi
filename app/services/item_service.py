from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_
from app.models.item import Item
from app.models.user import User
from app.models.category import Category
from app.schemas.item import ItemCreate, ItemUpdate


def list_items(db: Session, skip: int = 0, limit: int = 100, owner_id: int | None = None, q: str | None = None, category_id: int | None = None) -> list[Item]:
    query = db.query(Item).options(selectinload(Item.owner), selectinload(Item.categories))
    if owner_id is not None:
        query = query.filter(Item.owner_id == owner_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Item.title.like(like), Item.description.like(like)))
    if category_id is not None:
        query = query.join(Item.categories).filter(Category.id == category_id)
    return query.order_by(Item.id.asc()).offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int) -> Item | None:
    return db.query(Item).options(selectinload(Item.owner), selectinload(Item.categories)).filter(Item.id == item_id).first()


def create_item(db: Session, payload: ItemCreate) -> Item:
    owner = db.get(User, payload.owner_id)
    if not owner:
        raise ValueError("Owner no existe")
    item = Item(title=payload.title, description=payload.description, owner=owner)
    db.add(item)
    db.commit()
    db.refresh(item)
    # Asignar categorías si vienen en payload
    if getattr(payload, "category_ids", None):
        cats = db.query(Category).filter(Category.id.in_(payload.category_ids)).all()
        item.categories = cats
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


def update_item(db: Session, item_id: int, payload: ItemUpdate) -> Item | None:
    item = get_item(db, item_id)
    if not item:
        return None
    if payload.title is not None:
        item.title = payload.title
    if payload.description is not None:
        item.description = payload.description
    if payload.owner_id is not None:
        owner = db.get(User, payload.owner_id)
        if not owner:
            raise ValueError("Owner no existe")
        item.owner = owner
    # Reemplazar categorías si se especifica
    if getattr(payload, "category_ids", None) is not None:
        cats: list[Category] = []
        if payload.category_ids:
            cats = db.query(Category).filter(Category.id.in_(payload.category_ids)).all()
        item.categories = cats
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int) -> bool:
    item = get_item(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True