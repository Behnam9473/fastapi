from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..good.goods import GoodResponse

class OutboundBase(BaseModel):
    # seller_name: str
    purchase_price: float
    sale_price: float
    qty: int
    # tenant_id: UUID4 #tenant_id is a must
    file: Optional[str] = None
    published: Optional[bool] = False
class OutboundCreate(OutboundBase):
    good_id: int

class OutboundUpdate(OutboundBase):
    pass

class OutboundResponse(OutboundBase):
    id: int
    good: GoodResponse
    seller_name: str
    created_at: datetime

    class Config:
        from_attributes = True