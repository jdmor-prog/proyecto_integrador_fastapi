from sqlalchemy import Column, Integer, String, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


# Tabla de asociación M:N entre Item y Category
item_category = Table(
    "item_category",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True, index=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True, index=True),
    UniqueConstraint("item_id", "category_id", name="uq_item_category"),
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(300))

    # Relación M:N con Item mediante la tabla de asociación
    items = relationship(
        "Item",
        secondary=item_category,
        back_populates="categories",
    )