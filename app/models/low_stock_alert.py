from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class LowStockAlert(Base):
    __tablename__ = "low_stock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    comment = Column(String(500), nullable=True)

    product = relationship("Product", back_populates="alerts")
