from pydantic import BaseModel

class ColorBase(BaseModel):
    name: str
    code: str

class ColorCreate(ColorBase):
    pass

class ColorUpdate(ColorBase):
    pass

class ColorInDBBase(ColorBase):
    id: int

    class Config:
        from_attributes: True

class Color(ColorInDBBase):
    pass

class ColorInDB(ColorInDBBase):
    pass