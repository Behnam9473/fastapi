from typing import List, Optional
from sqlalchemy.orm import Session
from models.good.colors import Color as ColorModel
from schemas.good.colors import ColorCreate, ColorUpdate
from crud.base import CRUDBase


class ColorCRUD(CRUDBase[ColorModel, ColorCreate, ColorUpdate]):
    """
    CRUD operations for Color model.
    
    Provides basic CRUD operations (Create, Read, Update, Delete) for Color model.
    Inherits from CRUDBase which provides common CRUD functionality.
    """
    def get(self, db: Session, id: int) -> Optional[ColorModel]:
        """
        Get a single color by ID.
        
        Args:
            db: SQLAlchemy Session
            id: ID of the color to retrieve
            
        Returns:
            Optional[ColorModel]: Color object if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[ColorModel]:
        """
        Get multiple colors with pagination.
        
        Args:
            db: SQLAlchemy Session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            
        Returns:
            List[ColorModel]: List of Color objects
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ColorCreate) -> ColorModel:
        """
        Create a new color.
        
        Args:
            db: SQLAlchemy Session
            obj_in: ColorCreate schema with data for new color
            
        Returns:
            ColorModel: The created Color object
        """
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, id: int, obj_in: ColorUpdate) -> Optional[ColorModel]:
        """
        Update a color.
        
        Args:
            db: SQLAlchemy Session
            id: ID of the color to update
            obj_in: ColorUpdate schema with data to update
            
        Returns:
            Optional[ColorModel]: Updated Color object if found, None otherwise
        """
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in obj_in.model_dump().items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[ColorModel]:
        """
        Delete a color.
        
        Args:
            db: SQLAlchemy Session
            id: ID of the color to delete
            
        Returns:
            Optional[ColorModel]: Deleted Color object if found, None otherwise
        """
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

# Create a singleton instance
color = ColorCRUD(ColorModel)  # Singleton instance for Color CRUD operations