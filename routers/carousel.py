"""
Carousel Router Module

This module handles all carousel-related routes in the ZOHOOR-AR application.
It provides endpoints for managing carousel images displayed in the application's UI.

Features:
- CRUD operations for carousel images
- Role-based access control (SUPERUSER only for modifications)
- Pagination support
- Active/inactive image filtering
"""

# Standard library imports
import os
from typing import List

# Third-party imports
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status
)
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# CRUD operations
from crud.carousel import carousel

# Service layer
from services.redis.rate_limit import rate_limit
from services.save_images import save_image

# Schema definitions
from schemas.carousel import (
    CarouselImageCreate,
    CarouselImageUpdate,
    CarouselImageResponse
)

# Authentication utilities
from utils.auth import get_current_user

router = APIRouter(prefix="/carousel", tags=["Carousel"])

@router.post("/", response_model=CarouselImageResponse)
async def create_carousel_image(
    title: str = Form(...),  # Receive title from form data
    description: List[str] = Form(...),
    price: List[float] = Form(...),
    url: List[str] = Form(...),
    btn_x_coordinate: List[int] = Form(...),
    btn_y_coordinate: List[int] = Form(...),
    image_alternate_text: str = Form(...),  # Receive image_alternate_text from form data
    image:UploadFile = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _ = Depends(rate_limit),
):
    """
    Create a new carousel image.
    
    This endpoint allows SUPERUSER to add new images to the carousel.
    
    Args:
        image_in (CarouselImageCreate): Image data including URL and status
        db (Session): Database session dependency
        current_user (dict): Current authenticated user info
        
    Returns:
        CarouselImageResponse: Created carousel image data
        
    Raises:
        HTTPException: 403 if user is not SUPERUSER
        
    Security:
        Requires SUPERUSER role
    """
    if current_user['role'] != 'SUPERUSER':
        raise HTTPException(status_code=403, detail="Not authorized to create carousel images")
    # Create the CarouselImageCreate object without the image field
    # Create the CarouselImageCreate object with all required fields
    image_path = await save_image(image,"carousel", title)

    image_in = CarouselImageCreate(
        title=title,
        image=image_path,
        description=description,
        price=price,
        url=url,
        btn_x_coordinate=btn_x_coordinate,
        btn_y_coordinate=btn_y_coordinate,
        image_alternate_text=image_alternate_text  # Include this field
    )    
    # Await the save_image coroutine

    
    # Pass the image file to the service
    return carousel.create(db=db, image_data=image_in)

@router.get("/", response_model=List[CarouselImageResponse])
def read_carousel_images(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    _ = Depends(rate_limit),
):
    """
    Get all carousel images with pagination.
    
    This endpoint retrieves all carousel images, both active and inactive.
    
    Args:
        skip (int): Number of records to skip (default: 0)
        limit (int): Maximum number of records to return (default: 10)
        db (Session): Database session dependency
        
    Returns:
        List[CarouselImageResponse]: List of carousel images
        
    Note:
        This endpoint is publicly accessible
    """

    
    # Fetch data from the database using the carousel CRUD layer
    images = carousel.get_multi(db=db, skip=skip, limit=limit)
    
    return images


@router.get("/{carousel_id}", response_model=CarouselImageResponse)
def read_carousel_image(
    carousel_id: int = Path(..., title="The ID of the carousel image to get"),
    db: Session = Depends(get_db)
):
    """
    Get a specific carousel image by ID.
    
    Args:
        carousel_id (int): The unique identifier of the carousel image
        db (Session): Database session dependency
        
    Returns:
        CarouselImageResponse: Carousel image data
        
    Raises:
        HTTPException: 404 if image not found
        
    Note:
        This endpoint is publicly accessible
    """
    db_carousel = carousel.get(db=db, id=carousel_id)
    if db_carousel is None:
        raise HTTPException(status_code=404, detail="Carousel image not found")
    return db_carousel

@router.put("/{carousel_id}", response_model=CarouselImageResponse)
def update_carousel_image(
    carousel_id: int,
    carousel_in: CarouselImageUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a carousel image.
    
    This endpoint allows SUPERUSER to modify existing carousel images.
    
    Args:
        carousel_id (int): The unique identifier of the carousel image
        carousel_in (CarouselImageUpdate): Updated image data
        db (Session): Database session dependency
        current_user (dict): Current authenticated user info
        
    Returns:
        CarouselImageResponse: Updated carousel image data
        
    Raises:
        HTTPException: 403 if user is not SUPERUSER
        HTTPException: 404 if image not found
        
    Security:
        Requires SUPERUSER role
    """
    if current_user['role'] != 'SUPERUSER':
        raise HTTPException(status_code=403, detail="Not authorized to update carousel images")
    
    db_carousel = carousel.get(db=db, id=carousel_id)
    if db_carousel is None:
        raise HTTPException(status_code=404, detail="Carousel image not found")
    
    return carousel.update(db=db, db_obj=db_carousel, obj_in=carousel_in)

@router.delete("/{carousel_id}", response_model=CarouselImageResponse)
def delete_carousel_image(
    carousel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a carousel image.
    
    This endpoint allows SUPERUSER to remove carousel images.
    
    Args:
        carousel_id (int): The unique identifier of the carousel image
        db (Session): Database session dependency
        current_user (dict): Current authenticated user info
        
    Returns:
        CarouselImageResponse: Deleted carousel image data
        
    Raises:
        HTTPException: 403 if user is not SUPERUSER
        HTTPException: 404 if image not found
        
    Security:
        Requires SUPERUSER role
    """
    if current_user['role'] != 'SUPERUSER':
        raise HTTPException(status_code=403, detail="Not authorized to delete carousel images")
    
    db_carousel = carousel.get(db=db, id=carousel_id)
    if db_carousel is None:
        raise HTTPException(status_code=404, detail="Carousel image not found")
    
    return carousel.delete(db=db, id=carousel_id)