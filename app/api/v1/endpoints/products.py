# app/api/v1/endpoints/products.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate
from app.crud.product import (
    create_product,
    get_products,
    get_product_by_id,
    update_product,
    delete_product,
)
from app.api.deps import admin_required
from app.core.database import get_db
from app.core.security import get_current_active_user  # para roles USER/ADMIN access

router = APIRouter(prefix="/products", tags=["products"])


# Create product - ADMIN only
@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)])
def api_create_product(*, db: Session = Depends(get_db), product_in: ProductCreate):
    product = create_product(db=db, product_in=product_in)
    return product


# List products - USER or ADMIN
@router.get("/", response_model=List[ProductPublic])
def api_list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    products = get_products(db=db, skip=skip, limit=limit)
    return products


# Get product by id - USER or ADMIN
@router.get("/{product_id}", response_model=ProductPublic)
def api_get_product(product_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    product = get_product_by_id(db=db, product_id=product_id)
    if not product or not product.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/{product_id}", response_model=ProductPublic, dependencies=[Depends(admin_required)])
def api_update_product(product_id: int, updates: ProductUpdate, db: Session = Depends(get_db)):
    product = get_product_by_id(db=db, product_id=product_id)
    if not product or not product.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    product = update_product(db=db, product=product, updates=updates)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def api_delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db=db, product_id=product_id)
    if not product or not product.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    delete_product(db=db, product=product)
    return {"message": "Producto eliminado correctamente"}
