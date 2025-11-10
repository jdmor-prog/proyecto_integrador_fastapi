from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.schemas.item import ItemRead, ItemCreate, ItemUpdate, ItemReadWithOwner
from app.core.database import get_db
from app.services import item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[ItemReadWithOwner])
def list_items(skip: int = 0, limit: int = 100, owner_id: int | None = None, q: str | None = None, category_id: int | None = None, db: Session = Depends(get_db)):
    items = item_service.list_items(db, skip=skip, limit=limit, owner_id=owner_id, q=q, category_id=category_id)
    return items


@router.post("/", response_model=ItemReadWithOwner)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    new_item = item_service.create_item(db, item)
    return new_item


@router.get("/{item_id}", response_model=ItemReadWithOwner)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = item_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return item


@router.put("/{item_id}", response_model=ItemReadWithOwner)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    try:
        item = item_service.update_item(db, item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return item

# Actualización puntual con PATCH (parcial)
@router.patch("/{item_id}", response_model=ItemReadWithOwner)
def patch_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    try:
        item = item_service.update_item(db, item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return item



@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    ok = item_service.delete_item(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)