from pydantic import BaseModel, EmailStr
from enum import Enum
import uuid


class RoleEnum(str, Enum):
    CUSTOMER = "CUSTOMER"
    SUPERUSER = "SUPERUSER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: RoleEnum = RoleEnum.CUSTOMER


class UserCreate(UserBase):
    password: str
    tenant_id: uuid.UUID


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: RoleEnum | None = None
    tenant_id: uuid.UUID | None = None


class User(UserBase):
    id: int
    tenant_id: uuid.UUID | None = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    # tenant_id: uuid.UUID 

    class Config:
        from_attributes = True      
