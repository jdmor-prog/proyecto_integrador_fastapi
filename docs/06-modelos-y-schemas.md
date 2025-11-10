# 06 - Modelos (SQLAlchemy) y Schemas (Pydantic v2)

## Modelos ORM (SQLAlchemy)

`app/models/user.py`
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Relación ORM: un usuario tiene muchos ítems
    items = relationship(
        "Item",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Relación ORM 1:1 con Profile
    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
```

`app/models/item.py`
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Relación ORM: ítem pertenece a un usuario
    owner = relationship("User", back_populates="items")
```

- Estas clases mapean tablas `users` e `items` y declaran relaciones ORM explícitas.
- `User.items` y `Item.owner` permiten navegación bidireccional y borrado en cascada.

`app/models/profile.py`
```python
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_profiles_user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    bio = Column(String(500), nullable=True)
    phone = Column(String(30), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    user = relationship("User", back_populates="profile")
```

- `Profile` mantiene una relación uno a uno con `User` mediante `user_id` único.
- Al eliminar un `User`, su `Profile` se elimina por cascada.

## Schemas (Pydantic v2)

`app/schemas/user.py`
```python
from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
```

`app/schemas/item.py`
```python
from pydantic import BaseModel
from pydantic import ConfigDict

class ItemBase(BaseModel):
    title: str
    description: str | None = None
    owner_id: int

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    owner_id: int | None = None

class UserSummary(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class ItemReadWithOwner(ItemRead):
    owner: UserSummary
```

`app/schemas/profile.py`
```python
from pydantic import BaseModel
from pydantic import ConfigDict

class ProfileBase(BaseModel):
    bio: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    user_id: int

class ProfileCreate(ProfileBase):
    pass

class ProfileRead(ProfileBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ProfileUpdate(BaseModel):
    bio: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
```

`UserRead` con resumen de perfil opcional
```python
class ProfileSummary(BaseModel):
    id: int
    bio: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    model_config = ConfigDict(from_attributes=True)

class UserReadWithProfile(UserRead):
    profile: ProfileSummary | None = None
```

Claves de Pydantic v2:
- `ConfigDict(from_attributes=True)` permite construir el schema desde objetos ORM (`User`, `Item`) sin `.dict()` manual.
- `UserCreate` y `ItemCreate` representan payloads de creación.
- `UserRead` y `ItemRead` son respuestas de lectura.
- `ItemReadWithOwner` embebe el usuario dueño del ítem.
- `UserUpdate` y `ItemUpdate` permiten actualizaciones parciales.

Buenas prácticas:
- Mantén `*Create`, `*Read`, `*Update` separados para claridad.
- Usa `EmailStr` cuando requiera validación de correo.
- Evita exponer campos internos (como contraseñas) en `Read`.
- Usa relaciones ORM (`relationship`) para simplificar cargas y coherencia referencial.
- Para relaciones 1:1, usa `uselist=False` en `relationship` y una `UniqueConstraint` sobre la clave foránea.