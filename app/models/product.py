from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    barcode = Column(String(255), unique=True, index=True, nullable=False)
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=0)
    price = Column(Float, default=0)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True)

    warehouse = relationship("Warehouse", back_populates="products")
    stock_movements = relationship("StockMovement", back_populates="product")
    alerts = relationship("LowStockAlert", back_populates="product")
