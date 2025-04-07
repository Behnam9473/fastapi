"""
Color Router Module

This module provides API endpoints for managing color resources in the system.
It handles CRUD operations for colors with proper authentication and authorization checks.

Endpoints:
- POST /: Create a new color
- GET /: List all colors with pagination
- GET /{color_id}: Get a specific color by ID
- PUT /{color_id}: Update a color
- DELETE /{color_id}: Delete a color

All endpoints require authentication and restrict access to non-CUSTOMER roles.
"""
# Standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Local application imports
# Database related
from database import get_db

# Schema related
from schemas.good import colors as schemas

# Authentication related
from utils.auth import get_current_user

# CRUD operations
from crud.good.colors import color

router = APIRouter(prefix="/color", tags=["Color"])

@router.post("/", response_model=schemas.Color)
def create_color(
    color_in: schemas.ColorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new color.
    
    Args:
        color_in (schemas.ColorCreate): Color data to create
        db (Session): Database session
        current_user (dict): Authenticated user details
        
    Returns:
        schemas.Color: The created color
        
    Raises:
        HTTPException: 400 if color name already exists
        HTTPException: 403 if user doesn't have permission
    """
    if current_user['role'] != "CUSTOMER":
        try:
            return color.create(db=db, obj_in=color_in)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A color with this name already exists"
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )

@router.get("/", response_model=List[schemas.Color])
def read_colors(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a list of colors with pagination.
    
    Args:
        skip (int): Number of items to skip (default 0)
        limit (int): Maximum number of items to return (default 10)
        db (Session): Database session
        current_user (dict): Authenticated user details
        
    Returns:
        List[schemas.Color]: List of color objects
        
    Raises:
        HTTPException: 403 if user doesn't have permission
    """
    if current_user['role'] != "CUSTOMER":
        return color.get_multi(db, skip=skip, limit=limit)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )

@router.get("/{color_id}", response_model=schemas.Color)
def read_color(
    color_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific color by ID.
    
    Args:
        color_id (int): ID of the color to retrieve
        db (Session): Database session
        current_user (dict): Authenticated user details
        
    Returns:
        schemas.Color: The requested color
        
    Raises:
        HTTPException: 404 if color not found
        HTTPException: 403 if user doesn't have permission
    """
    if current_user['role'] != "CUSTOMER":
        db_color = color.get(db, id=color_id)
        if db_color is None:
            raise HTTPException(status_code=404, detail="Color not found")
        return db_color
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )

@router.put("/{color_id}", response_model=schemas.Color)
def update_color(
    color_id: int,
    color_in: schemas.ColorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing color.
    
    Args:
        color_id (int): ID of the color to update
        color_in (schemas.ColorUpdate): Updated color data
        db (Session): Database session
        current_user (dict): Authenticated user details
        
    Returns:
        schemas.Color: The updated color
        
    Raises:
        HTTPException: 404 if color not found
        HTTPException: 403 if user doesn't have permission
    """
    if current_user['role'] != "CUSTOMER":
        db_color = color.get(db, id=color_id)
        if db_color is None:
            raise HTTPException(status_code=404, detail="Color not found")
        return color.update(db=db, id=color_id, obj_in=color_in)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )

@router.delete("/{color_id}", response_model=schemas.Color)
def delete_color(
    color_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a color.
    
    Args:
        color_id (int): ID of the color to delete
        db (Session): Database session
        current_user (dict): Authenticated user details
        
    Returns:
        schemas.Color: The deleted color
        
    Raises:
        HTTPException: 404 if color not found
        HTTPException: 403 if user doesn't have permission
    """
    if current_user['role'] != "CUSTOMER":
        db_color = color.get(db, id=color_id)
        if db_color is None:
            raise HTTPException(status_code=404, detail="Color not found")
        return color.delete(db=db, id=color_id)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )