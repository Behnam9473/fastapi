from typing import List, Optional
from sqlalchemy.orm import Session
from models.good.colors import Color as ColorModel
from schemas.good.colors import ColorCreate, ColorUpdate
from crud.base import CRUDBase

# filepath: /C:/Users/KD/Desktop/Zohoor-AR/crud/good/colors.py

class ColorCRUD(CRUDBase[ColorModel, ColorCreate, ColorUpdate]):
    def get(self, db: Session, id: int) -> Optional[ColorModel]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[ColorModel]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ColorCreate) -> ColorModel:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, id: int, obj_in: ColorUpdate) -> Optional[ColorModel]:
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in obj_in.model_dump().items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[ColorModel]:
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

# Create a singleton instance
color = ColorCRUD(ColorModel)