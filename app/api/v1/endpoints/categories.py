from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.category import CategoryRead, CategoryCreate, CategoryUpdate, CategoryReadWithItems
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryReadWithItems])
def list_categories(skip: int = 0, limit: int = 100, q: str | None = None, db: Session = Depends(get_db)):
    cats = category_service.list_categories(db, skip=skip, limit=limit, q=q)
    return cats


@router.post("/", response_model=CategoryRead)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    try:
        cat = category_service.create_category(db, payload)
        return cat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category_id}", response_model=CategoryReadWithItems)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = category_service.get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    try:
        cat = category_service.update_category(db, category_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    ok = category_service.delete_category(db, category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)