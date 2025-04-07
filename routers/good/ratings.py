# Python standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local application imports
from database import get_db
from models.users.users import RoleEnum
from schemas.good.ratings import RatingCreate, RatingUpdate, RatingResponse
from utils.auth import get_current_user
from crud.good.rating import rating

router = APIRouter(prefix="/ratings", tags=["Ratings"])
"""
Ratings API Router

This router handles all operations related to product ratings including:
- Creating new ratings
- Retrieving product ratings
- Updating existing ratings
- Deleting ratings

All endpoints require authentication except for retrieving product ratings.
"""

@router.post("/{inventory_id}", response_model=RatingResponse)
def create_rating(
    inventory_id: int,
    rating_in: RatingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new product rating
    
    Args:
        inventory_id (int): ID of the inventory item being rated
        rating_in (RatingCreate): Rating data including score and optional comment
        
    Returns:
        RatingResponse: The created rating with all details
        
    Raises:
        HTTPException 403: If user is not a customer
        HTTPException 400: If rating data is invalid
    """
    if current_user['role'] == RoleEnum.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can rate products"
        )
    
    try:
        return rating.create(
            db=db,
            obj_in=rating_in,
            customer_id=current_user['user_id'],
            inventory_id=inventory_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/product/{inventory_id}", response_model=List[RatingResponse])
def get_product_ratings(
    inventory_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all ratings for a product
    
    Args:
        inventory_id (int): ID of the inventory item
        
    Returns:
        List[RatingResponse]: All ratings for the specified product
    """
    return rating.get_by_inventory(db, inventory_id)

@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    rating_update: RatingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an existing rating
    
    Args:
        rating_id (int): ID of the rating to update
        rating_update (RatingUpdate): Updated rating data
        
    Returns:
        RatingResponse: The updated rating with all details
        
    Raises:
        HTTPException 403: If user is not a customer
        HTTPException 404: If rating doesn't exist or user doesn't own it
    """
    if current_user['role'] == RoleEnum.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can update ratings"
        )
    
    # Verify ownership
    existing_rating = rating.get_user_rating(
        db, 
        customer_id=current_user['id'], 
        inventory_id=rating_id
    )
    if not existing_rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found or you don't have permission to update it"
        )
    
    return rating.update(db, id=rating_id, obj_in=rating_update)

@router.delete("/{rating_id}")
def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a rating
    
    Args:
        rating_id (int): ID of the rating to delete
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 403: If user is not a superuser
        HTTPException 404: If rating doesn't exist or user doesn't own it
    """
    if current_user['role'] == RoleEnum.SUPERUSER:
        raise HTTPException(
            status_code=403,
            detail="Only SUPERUSER can delete ratings"
        )
    
    # Verify ownership
    existing_rating = rating.get_user_rating(
        db, 
        customer_id=current_user['id'], 
        inventory_id=rating_id
    )
    if not existing_rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found or you don't have permission to delete it"
        )
    
    rating.delete(db, id=rating_id)
    return {"message": "Rating deleted successfully"}