# Python standard library imports
from typing import List
import uuid

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Models
from models.good.goods import Category

# Schemas
from schemas.good.goods import (
    CategorySelection,
    GoodCreate,
    GoodDecline,
    GoodUpdate,
    GoodResponse
)

# CRUD operations
from crud.good.goods import good

# Authentication utilities
from utils.auth import get_current_user, get_current_manager

# Service utilities
from services.save_images import save_images

# Initialize router with prefix and tags
router = APIRouter(prefix="/goods", tags=["Goods"])
def validate_category(session: Session, category_id: int):
    """
    Validate that the selected category is a leaf category.
    
    Args:
        session (Session): SQLAlchemy session
        category_id (int): ID of the category to validate
        
    Raises:
        HTTPException: If the category is invalid
    """
    if category_id:
        category = session.query(Category).get(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Use the corrected is_leaf property
        if not category.is_leaf:
            raise HTTPException(
                status_code=400,
                detail="Selected category must be a leaf category (category without subcategories)"
            )
# -------------------- Helper Functions --------------------

def check_admin_permissions(current_user: dict):
    """
    Helper function to check if user has admin permissions
    
    Args:
        current_user (dict): Dictionary containing user information including role
        
    Raises:
        HTTPException: 403 if user doesn't have required role
    """
    if current_user['role'] not in ["ADMIN", "MANAGER", "SUPERUSER"]:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

# -------------------- Create Operations --------------------

@router.post("/", response_model=GoodResponse)
async def create_good(
    name: str = Form(...),
    description: str = Form(...),
    weight: float = Form(...),
    length: int = Form(...),
    height: int = Form(...),
    parent_id: int = Form(...),
    subcategory_id: int = Form(...),
    colors: List[int] = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Create a new good with validation for category, colors, and images.
    
    Args:
        name: Name of the good
        description: Description of the good
        weight: Weight of the good
        length: Length of the good
        height: Height of the good
        parent_id: ID of parent category
        subcategory_id: ID of subcategory
        colors: List of color IDs
        images: List of uploaded image files
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        GoodResponse: The created good
        
    Raises:
        HTTPException: 403 if user lacks permissions
        HTTPException: 404 if category not found
        HTTPException: 400 if category is not a leaf
    """
    check_admin_permissions(current_user)
    tenant_id = uuid.UUID(current_user['tenant_id'])
    
    # Validate the selected subcategory
    validate_category(db, subcategory_id)
    
    # Create CategorySelection object
    category_selection = CategorySelection(
        parent_id=parent_id,
        subcategory_id=subcategory_id
    )
    
    # Create GoodCreate object from form data
    good_data = GoodCreate(
        name=name,
        description=description,
        weight=weight,
        length=length,
        height=height,
        colors=colors,
        category_selection=category_selection
    )

    # Save uploaded images
    good_data.images = await save_images(images, "goods")
    
    return good.validate_and_create(db=db, obj_in=good_data, tenant_id=tenant_id)

# # -------------------- Read Operations --------------------

@router.get("/inventory_goods/my_goods/", response_model=List[GoodResponse])
def get_my_goods(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Get all goods belonging to the current user's tenant.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[GoodResponse]: List of goods belonging to the tenant
        
    Raises:
        HTTPException: 403 if user lacks permissions
    """
    tenant_id = uuid.UUID(current_user['tenant_id'])
    return good.my_goods(db=db, tenant_id=tenant_id)

@router.get("/superuser_validated_goods/", response_model=List[GoodResponse])
def get_superuser_validated_goods(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all goods that have been validated by a superuser.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[GoodResponse]: List of validated goods
        
    Raises:
        HTTPException: 403 if user lacks permissions
    """
    check_admin_permissions(current_user)
    return good.get_superuser_validated_goods(db=db)

@router.get("/pending_goods/", response_model=List[GoodResponse])
def get_pending_goods(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all goods that are pending validation.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[GoodResponse]: List of pending goods
        
    Raises:
        HTTPException: 403 if user lacks permissions
    """
    check_admin_permissions(current_user)
    return good.get_pending_goods(db=db)

@router.get("/", response_model=List[GoodResponse])
def read_goods(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Get all goods with pagination support.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[GoodResponse]: Paginated list of goods
        
    Raises:
        HTTPException: 403 if user lacks permissions
    """
    check_admin_permissions(current_user)
    return good.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{good_id}", response_model=GoodResponse)
def read_good(
    good_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Get a specific good by ID.
    
    Args:
        good_id: ID of the good to retrieve
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        GoodResponse: The requested good
        
    Raises:
        HTTPException: 403 if user lacks permissions
        HTTPException: 404 if good not found
    """
    check_admin_permissions(current_user)
    db_good = good.get(db=db, id=good_id)
    if db_good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    return db_good

# -------------------- Update Operations --------------------

@router.put("/{good_id}", response_model=GoodResponse)
def update_good(
    good_id: int,
    good_data: GoodUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Update a good's information by ID.
    
    Args:
        good_id: ID of the good to update
        good_data: Updated good data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        GoodResponse: The updated good
        
    Raises:
        HTTPException: 403 if user lacks permissions
        HTTPException: 404 if good not found
    """
    check_admin_permissions(current_user)
    db_good = good.get(db=db, id=good_id)
    if db_good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    return good.update(db=db, db_obj=db_good, obj_in=good_data)

# -------------------- Delete Operations --------------------

@router.delete("/{good_id}", response_model=GoodResponse)
def delete_good(
    good_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Delete a good by ID.
    
    Args:
        good_id: ID of the good to delete
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        GoodResponse: The deleted good
        
    Raises:
        HTTPException: 403 if user lacks permissions
        HTTPException: 404 if good not found
    """
    check_admin_permissions(current_user)
    db_good = good.get(db=db, id=good_id)
    if db_good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    return good.remove(db=db, id=good_id)

# -------------------- Filter Operations --------------------

@router.get("/category/{category_id}", response_model=List[GoodResponse])
def read_goods_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Get goods filtered by category ID with pagination.
    
    Args:
        category_id: ID of the category to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[GoodResponse]: Paginated list of goods in category
        
    Raises:
        HTTPException: 403 if user lacks permissions
    """
    check_admin_permissions(current_user)
    return good.get_by_category(db=db, category_id=category_id, skip=skip, limit=limit)

@router.get("/color/{color_id}", response_model=List[GoodResponse])
def read_goods_by_color(
    color_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get goods filtered by color ID with pagination.
    
    Args:
        color_id: ID of the color to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[GoodResponse]: Paginated list of goods with color
        
    Raises:
        HTTPException: 403 if user lacks permissions
    """
    check_admin_permissions(current_user)
    return good.get_by_color(db=db, color_id=color_id, skip=skip, limit=limit)

# -------------------- Validation Operations --------------------

@router.post("/validate/{good_id}", response_model=GoodResponse)
def validate_good(
    good_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Validate a good by ID.
    Only superusers can perform this action.
    
    Args:
        good_id: ID of the good to validate
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        GoodResponse: The validated good
        
    Raises:
        HTTPException: 403 if user is not superuser
        HTTPException: 404 if good not found
    """
    if current_user['role'] not in ["SUPERUSER"]:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    db_good = good.get(db=db, id=good_id)
    if db_good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    return good.validate(db=db, id=good_id)

@router.post("/invalidate/{good_id}", response_model=GoodResponse)
def invalidate_good(
    good_id: int,
    decline_data: GoodDecline,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Invalidate a good by ID with a decline reason.
    Only superusers can perform this action.
    
    Args:
        good_id: ID of the good to invalidate
        decline_data: Reason for invalidation
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        GoodResponse: The invalidated good
        
    Raises:
        HTTPException: 403 if user is not superuser
        HTTPException: 404 if good not found
    """
    if current_user['role'] not in ["SUPERUSER"]:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    db_good = good.get(db=db, id=good_id)
    if db_good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    return good.invalidate(db=db, id=good_id, superuser_description=decline_data.superuser_description)