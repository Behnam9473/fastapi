# Standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Authentication and permissions
from utils.auth import get_current_manager
from routers.good.goods import check_admin_permissions

# CRUD operations
from crud.inventory.inventory import inventory

# Schema definitions
from schemas.inventory.inbound import (
    CustomizationCreate,
    CustomizationResponse,
    InboundCreate,
    InboundResponse,
    InboundUpdate
)

# Initialize router with prefix and tags
router = APIRouter(prefix="/inventory", tags=["Inventory"])

# ============= Inbound Inventory Endpoints =============

@router.get("", response_model=List[InboundResponse])
def read_inbounds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Retrieve all inbound inventory records with pagination.
    
    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        db (Session): Database session
        current_user (dict): Current authenticated user
    """
    check_admin_permissions(current_user)
    return inventory.get_inbounds(db=db, skip=skip, limit=limit)

@router.get("/inbound/{inbound_id}", response_model=InboundResponse)
def read_inbound(
    inbound_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Retrieve a specific inbound inventory record by ID with its customizations.
    
    Args:
        inbound_id (int): ID of the inbound record
        db (Session): Database session
        current_user (dict): Current authenticated user
    Returns:
        InboundResponse: Inbound record with associated customizations
    """
    check_admin_permissions(current_user)
    db_inbound = inventory.get_inbound(db=db, id=inbound_id)
    if db_inbound is None:
        raise HTTPException(status_code=404, detail="Inbound record not found")
    
    # The customizations will be automatically included in the response
    # because of the relationship defined in the Inventory model
    # and the InboundResponse schema
    return db_inbound

@router.post("/inbound", response_model=InboundResponse)
def create_inbound(
    inbound_data: InboundCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Create a new inbound inventory record.
    
    Args:
        inbound_data (InboundCreate): Inbound data to create
        db (Session): Database session
        current_user (dict): Current authenticated user
    """
    check_admin_permissions(current_user)
    seller_name = current_user['username']
    return inventory.create_inbound(db=db, obj_in=inbound_data, seller_name=seller_name)

@router.put("/{inbound_id}", response_model=InboundResponse)
def update_inbound(
    inbound_id: int,
    inbound_data: InboundUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Update an existing inbound inventory record.
    
    Args:
        inbound_id (int): ID of the inbound record to update
        inbound_data (InboundUpdate): Updated inbound data
        db (Session): Database session
        current_user (dict): Current authenticated user
    """
    check_admin_permissions(current_user)
    db_inbound = inventory.get_inbound(db=db, id=inbound_id)
    if db_inbound is None:
        raise HTTPException(status_code=404, detail="Inbound record not found")
    return inventory.update_inbound(db=db, db_obj=db_inbound, obj_in=inbound_data)

# ============= Customization Endpoints =============

@router.post("/{inventory_id}/customization/", response_model=CustomizationResponse)
def create_customization(
    inv_id: int,
    customization_data: CustomizationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Create a new customization for a specific good.
    
    Args:
        inv_id (int): ID of the good
        customization_data (CustomizationCreate): Customization data to create
        db (Session): Database session
        current_user (dict): Current authenticated user
    """
    check_admin_permissions(current_user)
    return inventory.create_customization(db=db, inv_id=inv_id, obj_in=customization_data)

@router.get("/{inventory_id}/customization/", response_model=List[CustomizationResponse])
def read_customizations(
    inv_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Retrieve all customizations for a specific good with pagination.
    
    Args:
        inv_id (int): ID of the good
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        db (Session): Database session
        current_user (dict): Current authenticated user
    """
    check_admin_permissions(current_user)
    return inventory.get_customizations(db=db, inv_id=inv_id, skip=skip, limit=limit)

@router.get("/{inventory_id}/customization/{customization_id}", response_model=CustomizationResponse)
def read_customization(
    inv_id: int,
    customization_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Retrieve a specific customization by ID.
    
    Args:
        good_id (int): ID of the good
        customization_id (int): ID of the customization
        db (Session): Database session
        current_user (dict): Current authenticated user
    """
    check_admin_permissions(current_user)
    db_customization = inventory.get_customization(db=db, inv_id=inv_id, id=customization_id)
    if db_customization is None:
        raise HTTPException(status_code=404, detail="Customization not found")
    return db_customization

@router.put("/{inventory_id}/customization/{customization_id}", response_model=CustomizationResponse)
def update_customization(
    inv_id: int,
    customization_id: int,
    customization_data: CustomizationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Update an existing customization.
    
    Args:
        good_id (int): ID of the good
        customization_id (int): ID of the customization to update
        customization_data (CustomizationCreate): Updated customization data
        db (Session): Database session
        current_user (dict): Current authenticated user
    """
    check_admin_permissions(current_user)
    db_customization = inventory.get_customization(db=db, inv_id=inv_id, id=customization_id)
    if db_customization is None:
        raise HTTPException(status_code=404, detail="Customization not found")
    return inventory.update_customization(db=db, db_obj=db_customization, obj_in=customization_data)

@router.delete("/{inventory_id}/customization/{customization_id}", response_model=CustomizationResponse)
def delete_customization(
    inv_id: int,
    customization_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    
    """
    Delete a customization.
    
    Args:
        inv_id (int): ID of the good
        customization_id (int): ID of the customization to delete
        db (Session): Database session
        current_user (dict): Current authenticated user
    """
    check_admin_permissions(current_user)
    db_customization = inventory.get_customization(db=db, inv_id=inv_id, id=customization_id)
    if db_customization is None:
        raise HTTPException(status_code=404, detail="Customization not found")
    return inventory.remove_customization(db=db, id=customization_id)
