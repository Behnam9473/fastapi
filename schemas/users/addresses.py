from pydantic import BaseModel
from typing import Optional

class AddressBase(BaseModel):
    province: str
    city: str
    street: str
    alley: str | None = None
    building: str | None = None
    number: int
    postal_code: str
    phone_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    province: str | None = None
    city: str | None = None
    street: str | None = None
    alley: str | None = None
    building: str | None = None
    number: int | None = None
    postal_code: str | None = None
    phone_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class Address(AddressBase):
    id: int
    customer_id: int

    class Config:
        from_attributes = True