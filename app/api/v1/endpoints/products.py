import csv
from io import StringIO
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import admin_required, user_or_admin_required, optional_current_user
from app.models import Product, Warehouse, StockMovement, MovementType, LowStockAlert, User
from app.schemas import ProductCreate, ProductUpdate, ProductOut, StockMovementCreate, StockMovementOut

router = APIRouter()


def _get_product_or_404(product_id: int, db: Session) -> Product:
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


def _ensure_low_stock_alert(db: Session, product: Product):
    if product.current_stock < product.minimum_stock:
        existing = (
            db.query(LowStockAlert)
            .filter(LowStockAlert.product_id == product.id, LowStockAlert.resolved.is_(False))
            .first()
        )
        if not existing:
            alert = LowStockAlert(product_id=product.id, comment="Stock por debajo del mínimo")
            db.add(alert)
    else:
        # Optionally resolve existing alerts when stock is ok
        db.query(LowStockAlert).filter(
            LowStockAlert.product_id == product.id, LowStockAlert.resolved.is_(False)
        ).update({"resolved": True})


@router.get("/", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), current_user: User | None = Depends(optional_current_user)):
    return db.query(Product).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User | None = Depends(optional_current_user)):
    return _get_product_or_404(product_id, db)


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(user_or_admin_required),
):
    if db.query(Product).filter(Product.barcode == payload.barcode).first():
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código de barras")
    if payload.warehouse_id:
        warehouse = db.query(Warehouse).get(payload.warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=404, detail="Almacén no encontrado")
    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    _ensure_low_stock_alert(db, product)
    db.commit()
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(user_or_admin_required),
):
    product = _get_product_or_404(product_id, db)
    update_data = payload.dict(exclude_unset=True)
    if "warehouse_id" in update_data and update_data["warehouse_id"]:
        warehouse = db.query(Warehouse).get(update_data["warehouse_id"])
        if not warehouse:
            raise HTTPException(status_code=404, detail="Almacén no encontrado")
    for key, value in update_data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    _ensure_low_stock_alert(db, product)
    db.commit()
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    product = _get_product_or_404(product_id, db)
    db.delete(product)
    db.commit()
    return None


@router.get("/export/csv")
def export_inventory_csv(db: Session = Depends(get_db), _: User = Depends(admin_required)):
    products = db.query(Product).all()
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "nombre", "descripcion", "codigo_barras", "almacen", "stock_actual", "stock_minimo", "precio"])
    for p in products:
        writer.writerow(
            [
                p.id,
                p.name,
                p.description or "",
                p.barcode,
                p.warehouse.name if p.warehouse else "",
                p.current_stock,
                p.minimum_stock,
                p.price,
            ]
        )
    buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=inventory.csv"}
    return StreamingResponse(buffer, media_type="text/csv", headers=headers)


@router.post("/{product_id}/stock/in", response_model=StockMovementOut)
def stock_in(
    product_id: int,
    payload: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_or_admin_required),
):
    product = _get_product_or_404(product_id, db)
    warehouse_id = payload.warehouse_id or product.warehouse_id
    movement = StockMovement(
        product_id=product.id,
        warehouse_id=warehouse_id,
        type=MovementType.ingreso,
        quantity=payload.quantity,
        user_id=current_user.id,
        comment=payload.comment,
    )
    product.current_stock += payload.quantity
    db.add(movement)
    _ensure_low_stock_alert(db, product)
    db.commit()
    db.refresh(movement)
    return movement


@router.post("/{product_id}/stock/out", response_model=StockMovementOut)
def stock_out(
    product_id: int,
    payload: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_or_admin_required),
):
    product = _get_product_or_404(product_id, db)
    if product.current_stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Stock insuficiente")
    warehouse_id = payload.warehouse_id or product.warehouse_id
    movement = StockMovement(
        product_id=product.id,
        warehouse_id=warehouse_id,
        type=MovementType.salida,
        quantity=payload.quantity,
        user_id=current_user.id,
        comment=payload.comment,
    )
    product.current_stock -= payload.quantity
    db.add(movement)
    _ensure_low_stock_alert(db, product)
    db.commit()
    db.refresh(movement)
    return movement


@router.get("/barcode/{barcode}", response_model=ProductOut)
def product_by_barcode(barcode: str, db: Session = Depends(get_db), current_user: User | None = Depends(optional_current_user)):
    product = db.query(Product).filter(Product.barcode == barcode).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.get("/stock/movements", response_model=list[StockMovementOut])
def list_movements(
    product_id: int | None = None,
    warehouse_id: int | None = None,
    type: MovementType | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    query = db.query(StockMovement)
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if warehouse_id:
        query = query.filter(StockMovement.warehouse_id == warehouse_id)
    if type:
        query = query.filter(StockMovement.type == type)
    query = query.order_by(StockMovement.date.desc())
    return query.all()
