from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import admin_required, user_or_admin_required
from app.schemas import WarehouseCreate, WarehouseUpdate, WarehouseOut
from app.models import Warehouse

router = APIRouter()


@router.post("/", response_model=WarehouseOut, status_code=status.HTTP_201_CREATED)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db), _: None = Depends(admin_required)):
    if db.query(Warehouse).filter(Warehouse.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Ya existe un almacén con ese nombre")
    warehouse = Warehouse(**payload.dict())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.get("/", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db), _: None = Depends(user_or_admin_required)):
    return db.query(Warehouse).all()


@router.get("/{warehouse_id}", response_model=WarehouseOut)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db), _: None = Depends(user_or_admin_required)):
    warehouse = db.query(Warehouse).get(warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    return warehouse


@router.patch("/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(admin_required),
):
    warehouse = db.query(Warehouse).get(warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(warehouse, key, value)
    db.commit()
    db.refresh(warehouse)
    return warehouse
