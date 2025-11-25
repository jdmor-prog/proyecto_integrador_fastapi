from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="warehouse")
    stock_movements = relationship("StockMovement", back_populates="warehouse")
