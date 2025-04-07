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
    """
    Create a new category
    
    Args:
        name: Name of the category (required)
        parent_id: ID of parent category if this is a subcategory (optional)
        image: Image file to associate with the category (optional)
        db: Database session dependency
        
    Returns:
        The created category with all its details
    
    Raises:
        HTTPException: If category creation fails
    """
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
    """
    Get all leaf categories (categories without children)
    
    Args:
        db: Database session dependency
        
    Returns:
        List of leaf categories with their IDs, names and full hierarchical paths
    
    Note:
        Leaf categories are typically used when selecting categories for goods
    """
    """Get all leaf categories that can be selected for goods"""
    leaf_categories = Category.get_leaf_categories(db)
    
    return [{
        "id": cat.id,
        "name": cat.name,
        "full_path": " > ".join([ancestor.name for ancestor in cat.get_ancestors(db)] + [cat.name])
    } for cat in leaf_categories]

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a single category by ID
    
    Args:
        category_id: ID of the category to retrieve
        db: Database session dependency
        
    Returns:
        The requested category with all its details
    
    Raises:
        HTTPException: If category is not found
    """
    crud = CategoryCRUD(db)
    return crud.get_by_id(category_id)

@router.get("/hierarchy/{category_id}", response_model=CategoryResponse)
def get_category_hierarchy(category_id: int, db: Session = Depends(get_db)):
    """
    Get a category with its complete hierarchy (parent and children)
    
    Args:
        category_id: ID of the root category to start from
        db: Database session dependency
        
    Returns:
        The category with its complete hierarchical structure
    
    Raises:
        HTTPException: If category is not found
    """
    crud = CategoryCRUD(db)
    return crud.get_hierarchy(category_id)

@router.get("/ancestors/{category_id}", response_model=List[CategoryResponse])
def get_ancestors(category_id: int, db: Session = Depends(get_db)):
    """
    Get all ancestor categories of a given category
    
    Args:
        category_id: ID of the category to find ancestors for
        db: Database session dependency
        
    Returns:
        List of ancestor categories in order from root to parent
    
    Raises:
        HTTPException: If category is not found
    """
    crud = CategoryCRUD(db)
    return crud.get_ancestors(category_id)

@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    """
    Get all categories in the system
    
    Args:
        db: Database session dependency
        
    Returns:
        List of all categories with their basic details
    """
    crud = CategoryCRUD(db)
    return crud.get_all()

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    """
    Update an existing category
    
    Args:
        category_id: ID of the category to update
        category_data: New data for the category
        db: Database session dependency
        
    Returns:
        The updated category with all its details
    
    Raises:
        HTTPException: If category is not found or update fails
    """
    crud = CategoryCRUD(db)
    return crud.update(category_id, category_data)

@router.delete("/{category_id}", response_model=CategoryResponse)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Delete a category
    
    Args:
        category_id: ID of the category to delete
        db: Database session dependency
        
    Returns:
        The deleted category details
    
    Raises:
        HTTPException: If category is not found or deletion fails
    """
    crud = CategoryCRUD(db)
    return crud.delete(category_id)


def build_category_tree(category):
    """
    Recursively build a tree structure of categories
    
    Args:
        category: The root category to build the tree from
        
    Returns:
        Dictionary representing the category tree with nested children
    """
    return {
        "id": category.id,
        "name": category.name,
        "children": [build_category_tree(child) for child in category.children] if category.children else []
    }



@router.get("/categories/tree", response_model=List[CategoryResponse])
def get_category_tree(db: Session = Depends(get_db)):
    """
    Get the complete category tree structure
    
    Args:
        db: Database session dependency
        
    Returns:
        List of root categories with their complete hierarchical structures
    """
    crud = CategoryCRUD(db)
    return crud.get_tree()

