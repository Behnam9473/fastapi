from pydantic import BaseModel, field_validator, validator
from typing import Any, List

class CarouselImageCreate(BaseModel):
    image_alternate_text: str
    description: List[str]
    price: List[float]
    url: List[str]
    btn_x_coordinate: List[int]
    btn_y_coordinate: List[int]
    image: str
    @validator("btn_x_coordinate", "btn_y_coordinate", each_item=True)
    def validate_coordinates(cls, v):
        if isinstance(v, str):
            try:
                return int(v.replace(",", ""))
            except ValueError:
                raise ValueError("Coordinate values must be integers.")
        elif isinstance(v, int):
            return v
        else:
            raise ValueError("Coordinate values must be integers or strings that can be converted to integers.")
        
class CarouselImageResponse(BaseModel):
    id: int
    image: str
    image_alternate_text: str
    description: List[str]
    btn_x_coordinate: List[int]
    btn_y_coordinate: List[int]
    price: List[float]
    url: List[str]

    class Config:
        from_attributes = True


class CarouselImageUpdate(BaseModel):
    # image: str
    image_alternate_text: str
    description: List[str]
    btn_x_coordinate: List[int]
    btn_y_coordinate: List[int]