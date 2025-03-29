from pydantic import BaseModel
from typing import ForwardRef, List, Optional, TYPE_CHECKING

# if TYPE_CHECKING:
#     from schemas import AttributeSet
Attribute = ForwardRef("Attribute")
class AttributeSetBase(BaseModel):
    name: str
    category_id: int

class AttributeSetCreate(AttributeSetBase):
    pass

class AttributeSet(AttributeSetBase):
    id: int
    attributes: List['Attribute'] = []

    class Config:
        from_attributes = True

class AttributeBase(BaseModel):
    name: str
    attribute_set_id: int
    data_type: str  # Could be further validated using Enum if required
    unit: Optional[str] = None

class AttributeCreate(AttributeBase):
    pass

class Attribute(AttributeBase):
    id: int

    class Config:
        from_attributes = True


class ProductAttributeValueBase(BaseModel):
    good_id: int
    attribute_id: int
    value_string: Optional[str] = None
    value_integer: Optional[int] = None
    value_float: Optional[float] = None
    value_boolean: Optional[bool] = None
    value_json: Optional[dict] = None

class ProductAttributeValueCreate(ProductAttributeValueBase):
    pass

class ProductAttributeValue(ProductAttributeValueBase):
    attribute: Optional[Attribute]

    class Config:
        from_attributes = True
