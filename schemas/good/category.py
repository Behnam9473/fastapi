from typing import List, Optional
from pydantic import BaseModel, field_validator

class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    image: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    children: List['CategoryResponse'] = []
    level: int = 0

    @field_validator('children', mode='before')
    def set_children(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return [item if isinstance(item, dict) else item.dict() for item in v]
        return []

    def calculate_levels(self, current_level: int = 0):
        """Recursively calculate levels for category and its children"""
        self.level = current_level
        for child in self.children:
            child.calculate_levels(current_level + 1)

    class Config:
        from_attributes = True

CategoryResponse.model_rebuild()