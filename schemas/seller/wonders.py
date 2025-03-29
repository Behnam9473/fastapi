from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from ..inventory.inbound import InboundResponse
# filepath: /C:/Users/KD/Desktop/Zohoor-AR/schemas/seller/wonders.py

class WondersCreate(BaseModel):
    inventory_id: int
    title: str
    description: Optional[str] = None
    is_active: bool = True
    percent_off: float
    start_date: datetime
    end_date: datetime 

class WondersUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    percent_off: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class WondersRead(BaseModel):
    id: int
    inventory: InboundResponse
    tenant_id: UUID
    title: str
    description: Optional[str] = None
    is_active: bool
    percent_off: float
    special_price: float
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True