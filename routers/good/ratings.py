# Python standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Models
from models.good.ratings import ProductRating
from models.inventory.inventory import Inventory
from models.users.users import RoleEnum

# Schemas
from schemas.good.ratings import (
    RatingCreate,
    RatingUpdate, 
    RatingResponse
)

# Authentication utilities
from utils.auth import get_current_user

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.post("/{inventory_id}", response_model=RatingResponse)
def create_rating(
    inventory_id: int,
    rating: RatingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new rating for a product"""
    # Check if user is a customer
    if current_user['role'] == RoleEnum.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can rate products"
        )
    
    # Check if inventory exists and is published
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id,
        Inventory.published == True
    ).first()
    
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Product not found or not available for rating"
        )
    
    # Check if user has already rated this product
    existing_rating = db.query(ProductRating).filter(
        ProductRating.customer_id == current_user['user_id'],
        ProductRating.inventory_id == inventory_id
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=400,
            detail="You have already rated this product"
        )
    
    # Create new rating
    db_rating = ProductRating(
        customer_id=current_user['user_id'],
        inventory_id=inventory_id,
        rating=rating.rating,
        comment=rating.comment
    )
    
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    
    return db_rating

@router.get("/product/{inventory_id}", response_model=List[RatingResponse])
def get_product_ratings(
    inventory_id: int,
    db: Session = Depends(get_db)
):
    """Get all ratings for a specific product"""
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id,
        Inventory.published == True
    ).first()
    
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Product not found or not available"
        )
    
    ratings = db.query(ProductRating).filter(
        ProductRating.inventory_id == inventory_id
    ).all()
    
    return ratings

@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    rating_update: RatingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing rating"""
    if current_user['role'] == RoleEnum.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can update ratings"
        )
    
    # Get existing rating
    db_rating = db.query(ProductRating).filter(
        ProductRating.id == rating_id,
        ProductRating.customer_id == current_user['id']
    ).first()
    
    if not db_rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found or you don't have permission to update it"
        )
    
    # Update rating fields
    if rating_update.rating is not None:
        db_rating.rating = rating_update.rating
    if rating_update.comment is not None:
        db_rating.comment = rating_update.comment
    
    db.commit()
    db.refresh(db_rating)
    
    return db_rating

@router.delete("/{rating_id}")
def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a rating"""
    if current_user['role'] == RoleEnum.SUPERUSER:
        raise HTTPException(
            status_code=403,
            detail="Only SUPERUSER can delete ratings"
        )
    
    # Get existing rating
    db_rating = db.query(ProductRating).filter(
        ProductRating.id == rating_id,
        ProductRating.customer_id == current_user['id']
    ).first()
    
    if not db_rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found or you don't have permission to delete it"
        )
    
    db.delete(db_rating)
    db.commit()
    
    return {"message": "Rating deleted successfully"} 