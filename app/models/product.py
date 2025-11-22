# app/models/product.py
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=0)
    id_categoria = Column(Integer, nullable=False)  # FK if you later add categories table
    id_almacen = Column(Integer, nullable=False)    # FK if you later add almacenes table
    codigo_barras = Column(String(128), nullable=True, index=True)
    activo = Column(Boolean, default=True)
