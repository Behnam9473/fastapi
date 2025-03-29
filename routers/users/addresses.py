"""
Address Management Router Module

This module handles all address-related operations in the ZOHOOR-AR application.
It provides endpoints for managing user addresses with role-based access control.

Features:
- CRUD operations for user addresses
- Role-based access control (user/admin)
- Address filtering by province and city
- Custom error handling
- Input validation
"""

# Standard library imports
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Schemas
from schemas.users import addresses as schemas

# Authentication
from utils.auth import get_current_user

# CRUD operations
from crud.users.addresses import AddressCRUD

# Exception handling
from utils.exceptions import AddressesError

router = APIRouter(
    prefix="/addresses",
    tags=['Addresses']
)

@router.post("/", response_model=schemas.Address)
def create_address(
    address: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new address for the current user.
    
    This endpoint allows users to add a new address to their profile.
    
    Args:
        address (AddressCreate): Address details to create
        db (Session): Database session dependency
        current_user (dict): Current authenticated user info
        
    Returns:
        Address: Created address information
        
    Raises:
        AddressesError: Custom error with type "CREATE_ERROR" if creation fails
        
    Security:
        - Requires authentication
        - Address is automatically associated with current user
    """
    try:
        crud = AddressCRUD(db)
        return crud.create(current_user['user_id'], address)
    except Exception as e:
        raise AddressesError(
            message=str(e),
            error_type="CREATE_ERROR",
            details={"address": address.model_dump()}
        )

@router.get("/", response_model=List[schemas.Address])
def get_addresses(
    province: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all addresses with optional filters.
    
    This endpoint retrieves addresses based on provided filters.
    Admins can see all addresses, while regular users only see their own.
    
    Args:
        province (str, optional): Filter by province name
        city (str, optional): Filter by city name
        db (Session): Database session dependency
        current_user (dict): Current authenticated user info
        
    Returns:
        List[Address]: List of matching addresses
        
    Raises:
        AddressesError: Custom error with type "FETCH_ERROR" if retrieval fails
        
    Security:
        - Requires authentication
        - Role-based access control (admin sees all, users see own)
    """
    try:
        crud = AddressCRUD(db)
        return crud.get_by_filters(
            user_id=current_user['user_id'],
            is_admin=current_user['role'] == "ADMIN",
            province=province,
            city=city
        )
    except Exception as e:
        raise AddressesError(
            message=str(e),
            error_type="FETCH_ERROR",
            details={"filters": {"province": province, "city": city}}
        )

@router.get("/{address_id}", response_model=schemas.Address)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific address by ID.
    
    This endpoint retrieves a single address by its ID.
    Users can only access their own addresses, while admins can access any address.
    
    Args:
        address_id (int): ID of the address to retrieve
        db (Session): Database session dependency
        current_user (dict): Current authenticated user info
        
    Returns:
        Address: Address information
        
    Raises:
        AddressesError: Custom error with type "FETCH_ERROR" if retrieval fails
        
    Security:
        - Requires authentication
        - Users can only access their own addresses
        - Admins can access any address
    """
    try:
        crud = AddressCRUD(db)
        return crud.get_by_id(
            address_id,
            current_user['user_id'],
            current_user['role'] == "ADMIN"
        )
    except Exception as e:
        raise AddressesError(
            message=str(e),
            error_type="FETCH_ERROR",
            details={"address_id": address_id}
        )

@router.put("/{address_id}", response_model=schemas.Address)
def update_address(
    address_id: int,
    address_update: schemas.AddressUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an address.
    
    This endpoint allows users to modify an existing address.
    Users can only update their own addresses, while admins can update any address.
    
    Args:
        address_id (int): ID of the address to update
        address_update (AddressUpdate): Updated address information
        db (Session): Database session dependency
        current_user (dict): Current authenticated user info
        
    Returns:
        Address: Updated address information
        
    Raises:
        AddressesError: Custom error with type "UPDATE_ERROR" if update fails
        
    Security:
        - Requires authentication
        - Users can only update their own addresses
        - Admins can update any address
    """
    try:
        crud = AddressCRUD(db)
        return crud.update(
            address_id,
            current_user['user_id'],
            address_update,
            current_user['role'] == "ADMIN"
        )
    except Exception as e:
        raise AddressesError(
            message=str(e),
            error_type="UPDATE_ERROR",
            details={
                "address_id": address_id,
                "update_data": address_update.model_dump()
            }
        )

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an address"""
    try:
        crud = AddressCRUD(db)
        crud.delete(
            address_id,
            current_user['user_id'],
            current_user['role'] == "ADMIN"
        )
    except Exception as e:
        raise AddressesError(
            message=str(e),
            error_type="DELETE_ERROR",
            details={"address_id": address_id}
        )