from typing import Optional
from pydantic import BaseModel


class WarehouseBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    active: Optional[bool] = None


class WarehouseOut(WarehouseBase):
    id: int

    class Config:
        from_attributes = True
