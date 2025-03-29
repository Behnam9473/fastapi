from pydantic import BaseModel, Field, confloat
from datetime import datetime
from typing import Optional

class RatingBase(BaseModel):
    # inventory_id: int
    rating: confloat(ge=1.0, le=5.0) = Field(..., description="Rating value between 1 and 5")
    comment: Optional[str] = Field(None, description="Optional comment about the rating")

class RatingCreate(RatingBase):
    pass

class RatingUpdate(BaseModel):
    rating: Optional[confloat(ge=1.0, le=5.0)] = Field(None, description="Rating value between 1 and 5")
    comment: Optional[str] = Field(None, description="Optional comment about the rating")

class RatingResponse(RatingBase):
    id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 