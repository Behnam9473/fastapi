# Standard library imports
from pathlib import Path
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import null
from sqlalchemy.orm import Session

# Local application imports
from database import get_db
from models.good.goods import Category  # Database models
from schemas.good.category import (  # Pydantic schemas
    CategoryCreate,
    CategoryResponse, 
    CategoryUpdate
)
from services.save_images import save_image  # Utility services
from crud.good.category import CategoryCRUD  # Database operations

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse)
async def create_category(
    name: str,
    parent_id: Optional[int] = None,
    image: Optional[UploadFile] = None,
    db: Session = Depends(get_db)
):
    # Save the image if provided
    relative_path = None
    if image:
        relative_path = await save_image(image, "categories", name)

    # Create category with image path
    category_data = CategoryCreate(
        name=name,
        parent_id=parent_id,
        image=relative_path
    )

    crud = CategoryCRUD(db)
    return crud.create(category_data)

@router.get("/leaf")
def get_leaf_categories(db: Session = Depends(get_db)):
    """Get all leaf categories that can be selected for goods"""
    leaf_categories = Category.get_leaf_categories(db)
    
    return [{
        "id": cat.id,
        "name": cat.name,
        "full_path": " > ".join([ancestor.name for ancestor in cat.get_ancestors(db)] + [cat.name])
    } for cat in leaf_categories]

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    crud = CategoryCRUD(db)
    return crud.get_by_id(category_id)

@router.get("/hierarchy/{category_id}", response_model=CategoryResponse)
def get_category_hierarchy(category_id: int, db: Session = Depends(get_db)):
    crud = CategoryCRUD(db)
    return crud.get_hierarchy(category_id)

@router.get("/ancestors/{category_id}", response_model=List[CategoryResponse])
def get_ancestors(category_id: int, db: Session = Depends(get_db)):
    crud = CategoryCRUD(db)
    return crud.get_ancestors(category_id)

@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    crud = CategoryCRUD(db)
    return crud.get_all()

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    crud = CategoryCRUD(db)
    return crud.update(category_id, category_data)

@router.delete("/{category_id}", response_model=CategoryResponse)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    crud = CategoryCRUD(db)
    return crud.delete(category_id)


def build_category_tree(category):
    """Recursively build a tree of categories"""
    return {
        "id": category.id,
        "name": category.name,
        "children": [build_category_tree(child) for child in category.children] if category.children else []
    }



@router.get("/categories/tree", response_model=List[CategoryResponse])
def get_category_tree(db: Session = Depends(get_db)):
    """Get the complete category tree"""
    crud = CategoryCRUD(db)
    return crud.get_tree()

