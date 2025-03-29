from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

from schemas.inventory.inbound import InboundResponse

class CartItem(BaseModel):
    item_id: int
    cart_id: UUID | None
    user_cart_id: UUID | None
    product_id: int
    # product: InboundResponse

    quantity: int
    price: float
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AnonymousCart(BaseModel):
    cart_id: UUID
    session_id: UUID
    items: list
    total_items: int
    total_price: float
    created_at: datetime
    expires_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AuthenticatedCart(BaseModel):
    cart_id: UUID
    user_id: int
    items: list
    total_items: int
    total_price: float
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CartItemResponse(CartItem):
    """Schema for cart item response including product details"""
    product: InboundResponse  # Include full product details from InboundResponse

    model_config = ConfigDict(from_attributes=True)
