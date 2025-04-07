# 1. Utility Functions
from pathlib import Path
import shutil
from typing import List, Optional

from fastapi import HTTPException, requests
from crud.base import CRUDBase
from models.carousel import CarouselImage
from schemas.carousel import CarouselImageCreate, CarouselImageUpdate
from sqlalchemy.orm import Session


class CRUDCarousel(CRUDBase[CarouselImage, CarouselImageCreate, CarouselImageUpdate]):
    """
    CRUD operations for CarouselImage model.
    
    Provides basic CRUD operations as well as custom methods for managing carousel images.
    Inherits from CRUDBase with CarouselImage model and related schemas.
    """
    # Basic CRUD operations
    def get(self, db: Session, id: int) -> Optional[CarouselImage]:
        """
        Get a single carousel image by ID.
        
        Args:
            db: SQLAlchemy Session
            id: ID of the carousel image to retrieve
            
        Returns:
            Optional[CarouselImage]: The carousel image if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[CarouselImage]:
        """
        Get multiple carousel images with pagination.
        
        Args:
            db: SQLAlchemy Session
            skip: Number of records to skip (default 0)
            limit: Maximum number of records to return (default 10)
            
        Returns:
            List[CarouselImage]: List of carousel images
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, image_data: CarouselImageCreate):
        """
        Create a new carousel image.
        
        Args:
            db: SQLAlchemy Session
            image_data: CarouselImageCreate schema with image data
            
        Returns:
            The created CarouselImage instance
        """
        db_image = CarouselImage(
            image=image_data.image,
            image_alternate_text=image_data.image_alternate_text,
            description=image_data.description,
            price=image_data.price,
            url=image_data.url,
            btn_x_coordinate=image_data.btn_x_coordinate,
            btn_y_coordinate=image_data.btn_y_coordinate,
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        return db_image
    
    def update(self, db: Session, *, id: int, obj_in: CarouselImageUpdate) -> Optional[CarouselImage]:
        """
        Update a carousel image.
        
        Args:
            db: SQLAlchemy Session
            id: ID of the carousel image to update
            obj_in: CarouselImageUpdate schema with updated data
            
        Returns:
            Optional[CarouselImage]: The updated carousel image if found, None otherwise
        """
        db_obj = self.get(db, id=id)
        if db_obj:
            update_data = obj_in.model_dump()
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: int) -> Optional[CarouselImage]:
        """
        Delete a carousel image.
        
        Also deletes the associated image file from storage.
        
        Args:
            db: SQLAlchemy Session
            id: ID of the carousel image to delete
            
        Returns:
            Optional[CarouselImage]: The deleted carousel image if found, None otherwise
        """
        db_obj = self.get(db, id=id)
        if db_obj:
            self._delete_image_file(db_obj.image)
            db.delete(db_obj)
            db.commit()
        return db_obj

    # Custom query methods
    def get_by_image_path(self, db: Session, *, image_path: str) -> Optional[CarouselImage]:
        """
        Get a carousel image by its image path.
        
        Args:
            db: SQLAlchemy Session
            image_path: Path of the image to search for
            
        Returns:
            Optional[CarouselImage]: The carousel image if found, None otherwise
        """
        return db.query(CarouselImage).filter(CarouselImage.image == image_path).first()
    


    # Helper methods
    def _delete_image_file(self, image_path: str) -> None:
        """
        Delete the physical image file from storage.
        
        Args:
            image_path: Path to the image file to delete
            
        Note:
            This is an internal helper method and should not be called directly.
        """
        path = Path(image_path)
        if path.exists():
            path.unlink()

# 3. Instance Creation
carousel = CRUDCarousel(CarouselImage)
