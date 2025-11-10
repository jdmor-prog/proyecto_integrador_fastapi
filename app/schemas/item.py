from pydantic import BaseModel
from pydantic import ConfigDict


class ItemBase(BaseModel):
    title: str
    description: str | None = None
    owner_id: int


class ItemCreate(ItemBase):
    # IDs de categorías a asociar al crear
    category_ids: list[int] | None = None


class ItemRead(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    owner_id: int | None = None
    # Reemplazar categorías del ítem
    category_ids: list[int] | None = None


# Resumen de usuario para embebido en ítem (evita import circular)
class UserSummary(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class ItemReadWithOwner(ItemRead):
    owner: UserSummary
    # Resumen de categorías embebidas
    class CategorySummary(BaseModel):
        id: int
        name: str
        model_config = ConfigDict(from_attributes=True)

    categories: list[CategorySummary] = []