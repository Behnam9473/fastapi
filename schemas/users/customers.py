from pydantic import BaseModel, EmailStr
from typing import List
from .addresses import Address


class CustomerBase(BaseModel):
    username: str
    email: EmailStr


class CustomerCreate(CustomerBase):
    password: str


class CustomerUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class CustomerResponse(CustomerBase):
    id: int
    username: str
    email: str  # Add this field
    addresses: List[Address] = []
    role: str
    class Config:
        from_attributes = True      


