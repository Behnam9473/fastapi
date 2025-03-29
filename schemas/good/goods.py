from typing import List, Optional, ClassVar
from uuid import UUID
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum

from .category import CategoryResponse

class Status(str, Enum):
    APPROVED = "approved"
    DECLINED = "declined"
    PENDING = "pending"

    def update_status(self, is_validated: bool, superuser_description: str = None) -> 'Status':
        if is_validated:
            return Status.APPROVED
        elif not is_validated and superuser_description:
            return Status.DECLINED
        else:
            return Status.PENDING

class CategorySelection(BaseModel):
    """Schema for category selection with parent and child categories"""
    parent_id: int = Field(..., description="ID of the parent category")
    subcategory_id: int = Field(..., description="ID of the selected subcategory")


class GoodBase(BaseModel):
    """Base schema for Good with common attributes."""
    name: str = Field(..., description="Name of the good")
    description: str = Field(..., description="Description of the good")
    weight: float = Field(..., description="Weight of the good in grams")
    length: int = Field(..., description="Length of the good in centimeters")
    height: int = Field(..., description="Height of the good in centimeters")

class GoodCreate(GoodBase):
    """Schema for creating a new Good."""
    colors: List[int] = Field(..., description="List of color IDs for this good")
    images: List[str] = Field(default_factory=list, description="List of image URLs for this good")
    category_selection: CategorySelection = Field(..., description="Category and subcategory selection")

    @field_validator('category_selection')
    def validate_category_hierarchy(cls, v, values):
        """Validate that the selected subcategory belongs to the parent category"""
        from models.good.goods import Category  # Import here to avoid circular imports
        from database import db  # Import the database instance instead of SessionLocal

        with db.get_session() as session:
            # Get the subcategory
            subcategory = session.query(Category).get(v.subcategory_id)
            if not subcategory:
                raise HTTPException(status_code=400, detail="Selected subcategory does not exist")

            # Verify parent relationship
            if subcategory.parent_id != v.parent_id:
                raise HTTPException(
                    status_code=400, 
                    detail="Selected subcategory does not belong to the specified parent category"
                )



            return v

    @property
    def category_id(self) -> int:
        """Get the actual category_id for the Good model"""
        return self.category_selection.subcategory_id
class GoodUpdate(BaseModel):
    """Schema for updating an existing Good."""
    name: Optional[str] = Field(None, description="Name of the good")
    description: Optional[str] = Field(None, description="Description of the good")
    weight: Optional[float] = Field(None, description="Weight of the good in grams")
    length: Optional[int] = Field(None, description="Length of the good in centimeters")
    height: Optional[int] = Field(None, description="Height of the good in centimeters")
    # category_id: Optional[int] = Field(None, description="ID of the category this good belongs to")
    colors: Optional[List[int]] = Field(None, description="List of color IDs for this good")
    images: Optional[List[str]] = Field(None, description="List of image URLs for this good")
    customizations: Optional[List[int]] = Field(None, description="List of customization IDs")
    superuser_description: Optional[str] = Field(None, description="Superuser description of the good")
    is_validated: bool = Field(default=False, description="Whether the good is validated by the superuser")

class GoodDecline(BaseModel):
    """Schema for declining a Good."""
    superuser_description: str = Field(..., description="Superuser description of the good")

class GoodResponse(GoodBase):
    """Schema for Good response including database fields."""
    id: int
    images: List[str]
    superuser_description: Optional[str] = Field(None, description="Superuser description of the good")
    is_validated: bool = Field(default=False, description="Whether the good is validated by the superuser")
    category: Optional[CategoryResponse] = Field(None, description="Category details of the good")
    created_at: datetime
    updated_at: datetime
    status: Status = Field(default=Status.PENDING, description="Status of the good")
    sku: Optional[str] = Field(None, description="Stock Keeping Unit of the good")

    class Config:
        from_attributes = True
