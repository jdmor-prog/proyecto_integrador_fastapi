from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Relación ORM con Item
    items = relationship(
        "Item",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # Hashed password using bcrypt; never store plain passwords
    hashed_password = Column(String(255), nullable=False)
    # Role: 'admin', 'user', or 'guest'
    role = Column(String(20), nullable=False, default="user")

    # Relación uno a uno con Profile
    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )