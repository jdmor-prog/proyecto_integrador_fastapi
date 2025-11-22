from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: str = "user"


class UserRead(UserBase):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None


class ItemSummary(BaseModel):
    id: int
    title: str
    description: str | None = None
    owner_id: int
    model_config = ConfigDict(from_attributes=True)


class UserReadWithItems(UserRead):
    items: list[ItemSummary] = []

class ProfileSummary(BaseModel):
    id: int
    bio: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class UserReadWithProfile(UserRead):
    profile: ProfileSummary | None = None

class UserReadFull(UserRead):
    items: list[ItemSummary] = []
    profile: ProfileSummary | None = None