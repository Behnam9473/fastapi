from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from typing import List, Optional

from models.users.addresses import Address
from schemas.users import addresses as schemas
from utils.exceptions import AddressError


class AddressCRUD:
    """
    CRUD operations for managing user addresses in the database.
    
    Provides methods for creating, reading, updating and deleting addresses
    with proper authorization checks and data validation.
    """
    def __init__(self, db: Session):
        self.db = db

    def _get_address_or_404(self, address_id: int) -> Address:
        """
        Internal method to retrieve an address by ID or raise 404 if not found.
        
        Args:
            address_id: The ID of the address to retrieve
            
        Returns:
            Address: The found address object
            
        Raises:
            HTTPException: 404 if address not found
        """
        address = self.db.query(Address).filter(Address.id == address_id).first()
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        return address

    def _check_authorization(self, address: Address, user_id: int, is_admin: bool) -> None:
        """
        Internal method to verify user authorization for address access.
        
        Args:
            address: The address object to check
            user_id: ID of the requesting user
            is_admin: Whether the user has admin privileges
            
        Raises:
            HTTPException: 403 if user is not authorized
        """
        if not is_admin and address.customer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this address"
            )

    def create(self, user_id: int, address_data: schemas.AddressCreate) -> Address:
        """
        Create a new address for the specified user.
        
        Args:
            user_id: ID of the user creating the address
            address_data: Address creation data from request
            
        Returns:
            Address: The newly created address object
            
        Raises:
            HTTPException: 400 if validation fails
        """
        try:
            # Validate address data
            Address.validate_postal_code(address_data.postal_code)
            if address_data.phone_number:
                Address.validate_phone_number(address_data.phone_number)
            if address_data.latitude or address_data.longitude:
                Address.validate_coordinates(address_data.latitude, address_data.longitude)

            # Create address
            address = Address(**address_data.model_dump(), customer_id=user_id)
            self.db.add(address)
            self.db.commit()
            self.db.refresh(address)
            return address
        except AddressError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def get_all(self, user_id: int, is_admin: bool = False) -> List[Address]:
        """
        Retrieve all addresses for a user (or all addresses if admin).
        
        Args:
            user_id: ID of the requesting user
            is_admin: Whether to bypass user filtering
            
        Returns:
            List[Address]: List of address objects
        """
        query = self.db.query(Address)
        if not is_admin:
            query = query.filter(Address.customer_id == user_id)
        return query.all()

    def get_by_id(self, address_id: int, user_id: int, is_admin: bool = False) -> Address:
        """
        Retrieve a specific address by ID with authorization check.
        
        Args:
            address_id: ID of the address to retrieve
            user_id: ID of the requesting user
            is_admin: Whether to bypass authorization check
            
        Returns:
            Address: The requested address object
            
        Raises:
            HTTPException: 404 if address not found
            HTTPException: 403 if unauthorized
        """
        address = self._get_address_or_404(address_id)
        self._check_authorization(address, user_id, is_admin)
        return address

    def update(self, address_id: int, user_id: int, address_data: schemas.AddressUpdate, is_admin: bool = False) -> Address:
        """
        Update an existing address with new data.
        
        Args:
            address_id: ID of the address to update
            user_id: ID of the requesting user
            address_data: New address data from request
            is_admin: Whether to bypass authorization check
            
        Returns:
            Address: The updated address object
            
        Raises:
            HTTPException: 404 if address not found
            HTTPException: 403 if unauthorized
            HTTPException: 400 if validation fails
        """
        try:
            address = self._get_address_or_404(address_id)
            self._check_authorization(address, user_id, is_admin)

            # Validate updated data if provided
            if address_data.postal_code:
                Address.validate_postal_code(address_data.postal_code)
            if address_data.phone_number:
                Address.validate_phone_number(address_data.phone_number)
            if address_data.latitude is not None or address_data.longitude is not None:
                Address.validate_coordinates(
                    address_data.latitude if address_data.latitude is not None else address.latitude,
                    address_data.longitude if address_data.longitude is not None else address.longitude
                )

            # Update address
            update_data = address_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(address, key, value)

            self.db.commit()
            self.db.refresh(address)
            return address
        except AddressError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def delete(self, address_id: int, user_id: int, is_admin: bool = False) -> None:
        """
        Delete an address with authorization check.
        
        Args:
            address_id: ID of the address to delete
            user_id: ID of the requesting user
            is_admin: Whether to bypass authorization check
            
        Raises:
            HTTPException: 404 if address not found
            HTTPException: 403 if unauthorized
        """
        address = self._get_address_or_404(address_id)
        self._check_authorization(address, user_id, is_admin)
        
        self.db.delete(address)
        self.db.commit()

    def get_by_filters(
        self,
        user_id: int,
        is_admin: bool = False,
        province: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Address]:
        """
        Retrieve addresses with optional province and city filters.
        
        Args:
            user_id: ID of the requesting user
            is_admin: Whether to bypass user filtering
            province: Optional province filter
            city: Optional city filter
            
        Returns:
            List[Address]: Filtered list of address objects
        """
        query = self.db.query(Address)
        
        if not is_admin:
            query = query.filter(Address.customer_id == user_id)
        
        filters = []
        if province:
            filters.append(Address.province == province)
        if city:
            filters.append(Address.city == city)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.all()
