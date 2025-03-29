from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..good.goods import GoodResponse

class CustomizationBase(BaseModel):
    """Base schema for Customization."""
    name: str = Field(..., description="Name of the customization")
    images: List[str] = Field(default_factory=list, description="List of image URLs for the customization")
    alternative_text: List[str] = Field(default_factory=list, description="List of alternative texts")
    prices: List[float] = Field(default_factory=list, description="List of prices")

class CustomizationCreate(CustomizationBase):
    """Schema for creating a new Customization."""
    pass

class CustomizationResponse(CustomizationBase):
    """Schema for Customization response including database fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InboundBase(BaseModel):
    # seller_name: str
    purchase_price: float
    sale_price: float
    qty: int
    # tenant_id: UUID4 #tenant_id is a must
    file: Optional[str] = None
    published: Optional[bool] = False
class InboundCreate(InboundBase):
    good_id: int
    customizations: Optional[List[int]] = Field(default_factory=list, description="List of customization IDs")

class InboundUpdate(InboundBase):
    pass

class InboundResponse(InboundBase):
    id: int
    good: GoodResponse
    seller_name: str
    created_at: datetime
    customizations: List[CustomizationResponse]

    class Config:
        from_attributes = True





