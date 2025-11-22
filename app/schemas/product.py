from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    stock: int
    stock_minimo: int
    id_categoria: int
    id_almacen: int
    codigo_barras: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    id_categoria: Optional[int] = None
    id_almacen: Optional[int] = None
    codigo_barras: Optional[str] = None


class ProductPublic(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    stock: int
    stock_minimo: int
    id_categoria: int
    id_almacen: int
    codigo_barras: Optional[str]

    class Config:
        from_attributes = True
