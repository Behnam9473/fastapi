from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
from enum import Enum

class RoleEnum(str, Enum):
    CUSTOMER = "CUSTOMER"
    SUPERUSER = "SUPERUSER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class ManagerBase(BaseModel):
    username: str
    email: EmailStr
    role: RoleEnum = RoleEnum.MANAGER
    tenant_id: UUID
    shop_name: str = None

class ManagerCreate(ManagerBase):
    password: str

class ManagerUpdate(BaseModel):
    shop_name: str = None

class ManagerResponse(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True      




class AdminBase(BaseModel):
    username: str
    email: EmailStr
    role: RoleEnum = RoleEnum.ADMIN
    tenant_id: UUID = None

class AdminCreate(AdminBase):
    password: str  # Plain password, will be hashed before storing

class AdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    tenant_id: Optional[UUID] = None

class AdminRead(AdminBase):
    id: int

    class Config:
        from_attributes = True