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
    if current_user['role'] != "CUSTOMER":
        db_color = color.get(db, id=color_id)
        if db_color is None:
            raise HTTPException(status_code=404, detail="Color not found")
        return color.delete(db=db, id=color_id)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )