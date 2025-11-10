from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Campos de perfil (personaliza según necesidades)
    bio = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    avatar_url = Column(String(255), nullable=True)

    # Relación uno a uno hacia User
    user = relationship("User", back_populates="profile")

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_profiles_user_id"),
    )