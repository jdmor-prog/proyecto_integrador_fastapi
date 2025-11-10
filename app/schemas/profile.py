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
    user_id: int | None = None

# Resumen de usuario para embebido en perfil (evita import circular)
class UserSummary(BaseModel):
    id: int
    name: str
    email: str
    role: str
    model_config = ConfigDict(from_attributes=True)

class ProfileReadWithUser(ProfileRead):
    user: UserSummary