from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    barcode: str
    current_stock: int = 0
    minimum_stock: int = 0
    price: float = 0
    warehouse_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    barcode: Optional[str] = None
    current_stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    price: Optional[float] = None
    warehouse_id: Optional[int] = None


class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True


class StockMovementCreate(BaseModel):
    quantity: int = Field(gt=0)
    warehouse_id: Optional[int] = None
    comment: Optional[str] = None


class StockMovementOut(BaseModel):
    id: int
    product_id: int
    warehouse_id: Optional[int]
    type: str
    quantity: int
    date: str
    user_id: Optional[int]
    comment: Optional[str]

    class Config:
        from_attributes = True


class LowStockAlertOut(BaseModel):
    id: int
    product_id: int
    created_at: str
    resolved: bool
    comment: Optional[str]

    class Config:
        from_attributes = True
