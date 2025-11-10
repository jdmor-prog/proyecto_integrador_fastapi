from pydantic import BaseModel
from pydantic import ConfigDict


class CategoryBase(BaseModel):
    name: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


# Resumen de ítem para embebido en categoría (evita import circular)
class ItemSummaryForCategory(BaseModel):
    id: int
    title: str
    description: str | None = None
    owner_id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryReadWithItems(CategoryRead):
    items: list[ItemSummaryForCategory] = []