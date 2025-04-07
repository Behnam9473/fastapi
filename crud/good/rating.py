from typing import List, Optional
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.good.ratings import ProductRating
from models.inventory.inventory import Inventory
from schemas.good.ratings import RatingCreate, RatingUpdate

class CRUDRating(CRUDBase[ProductRating, RatingCreate, RatingUpdate]):
    """
    CRUD operations for ProductRating model.
    
    Inherits from CRUDBase with ProductRating model, RatingCreate and RatingUpdate schemas.
    """
    def get(self, db: Session, id: int) -> Optional[ProductRating]:
        """
        Get a single rating by its ID.
        
        Args:
            db: SQLAlchemy Session
            id: Rating ID to retrieve
            
        Returns:
            Optional[ProductRating]: The rating if found, else None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[ProductRating]:
        """
        Get multiple ratings with pagination.
        
        Args:
            db: SQLAlchemy Session
            skip: Number of ratings to skip (default 0)
            limit: Maximum number of ratings to return (default 10)
            
        Returns:
            List[ProductRating]: List of ratings
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_by_inventory(self, db: Session, inventory_id: int) -> List[ProductRating]:
        """
        Get all ratings for a specific inventory item.
        
        Args:
            db: SQLAlchemy Session
            inventory_id: ID of the inventory item
            
        Returns:
            List[ProductRating]: List of ratings for the inventory item
        """
        return db.query(self.model).filter(
            self.model.inventory_id == inventory_id
        ).all()

    def create(self, db: Session, *, obj_in: RatingCreate, customer_id: int, inventory_id: int) -> ProductRating:
        """
        Create a new product rating.
        
        Args:
            db: SQLAlchemy Session
            obj_in: RatingCreate schema with rating data
            customer_id: ID of the customer creating the rating
            inventory_id: ID of the inventory item being rated
            
        Returns:
            ProductRating: The created rating
            
        Raises:
            ValueError: If product is not found/available or user has already rated
        """
        # Check if inventory exists and is published
        inventory = db.query(Inventory).filter(
            Inventory.id == inventory_id,
            Inventory.published == True
        ).first()
        
        if not inventory:
            raise ValueError("Product not found or not available for rating")
        
        # Check if user has already rated this product
        existing_rating = db.query(self.model).filter(
            self.model.customer_id == customer_id,
            self.model.inventory_id == inventory_id
        ).first()
        
        if existing_rating:
            raise ValueError("User has already rated this product")

        db_obj = ProductRating(
            customer_id=customer_id,
            inventory_id=inventory_id,
            rating=obj_in.rating,
            comment=obj_in.comment
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, id: int, obj_in: RatingUpdate) -> Optional[ProductRating]:
        """
        Update a product rating.
        
        Args:
            db: SQLAlchemy Session
            id: ID of the rating to update
            obj_in: RatingUpdate schema with updated data
            
        Returns:
            Optional[ProductRating]: The updated rating if found, else None
        """
        db_obj = self.get(db, id)
        if not db_obj:
            return None
            
        if obj_in.rating is not None:
            db_obj.rating = obj_in.rating
        if obj_in.comment is not None:
            db_obj.comment = obj_in.comment
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[ProductRating]:
        """
        Delete a product rating.
        
        Args:
            db: SQLAlchemy Session
            id: ID of the rating to delete
            
        Returns:
            Optional[ProductRating]: The deleted rating if found, else None
        """
        db_obj = self.get(db, id)
        if not db_obj:
            return None
            
        db.delete(db_obj)
        db.commit()
        return db_obj

    def get_user_rating(self, db: Session, *, customer_id: int, inventory_id: int) -> Optional[ProductRating]:
        """
        Get a user's rating for a specific inventory item.
        
        Args:
            db: SQLAlchemy Session
            customer_id: ID of the customer
            inventory_id: ID of the inventory item
            
        Returns:
            Optional[ProductRating]: The rating if found, else None
        """
        return db.query(self.model).filter(
            self.model.customer_id == customer_id,
            self.model.inventory_id == inventory_id
        ).first()

rating = CRUDRating(ProductRating)  # Instance of CRUDRating for direct use