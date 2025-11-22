from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

def create_product(db: Session, product_in: ProductCreate) -> Product:
    product = Product(
        nombre=product_in.nombre,
        descripcion=product_in.descripcion,
        stock=product_in.stock,
        stock_minimo=product_in.stock_minimo,
        id_categoria=product_in.id_categoria,
        id_almacen=product_in.id_almacen,
        codigo_barras=product_in.codigo_barras,
        activo=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    return db.query(Product).filter(Product.activo == True).offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_barcode(db: Session, barcode: str) -> Optional[Product]:
    return db.query(Product).filter(Product.codigo_barras == barcode).first()

def update_product(db: Session, product: Product, updates: ProductUpdate) -> Product:
    # update only provided fields
    for field, value in updates.__dict__.items():
        if value is not None:
            setattr(product, field, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product: Product) -> None:
    product.activo = False
    db.add(product)
    db.commit()
