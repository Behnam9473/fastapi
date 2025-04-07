import uuid
from sqlalchemy import UUID, Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from database import Base
from utils.exceptions import CustomerError, AuthenticationError, PermissionError
import re

# Import models after Base to avoid circular imports
from models.good.ratings import ProductRating
from sqlalchemy.dialects.postgresql import ENUM

# Define the Python Enum
class RoleEnum(PyEnum):
    """
    Enum representing user roles in the system.
    
    Attributes:
        CUSTOMER: Standard user role with basic permissions
        SUPERUSER: Elevated user role with additional permissions
        MANAGER: Role for shop managers with limited admin privileges
        ADMIN: Full system administrator role
    """
    CUSTOMER = "CUSTOMER"
    SUPERUSER = "SUPERUSER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

role_enum_type = ENUM(RoleEnum, name="role_enum")

class BaseUser(Base):
    """
    Abstract base class for all user types in the system.
    
    Provides common fields and validation methods for all user models.
    
    Attributes:
        id: Primary key
        username: Unique username
        email: Unique email address
        hashed_password: Securely stored password hash
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    @staticmethod
    def validate_username(username: str) -> None:
        """
        Validate username format according to system requirements.
        
        Args:
            username: The username to validate
            
        Raises:
            CustomerError: If username doesn't match required format
                - Error type: INVALID_USERNAME
                - Details: Contains username and format requirements
        """
        if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', username):
            raise CustomerError(
                message="Invalid username format",
                error_type="INVALID_USERNAME",
                details={
                    "username": username,
                    "requirements": "3-50 characters, alphanumeric, underscore, and hyphen only"
                }
            )

    @staticmethod
    def validate_email(email: str) -> None:
        """
        Validate email format according to standard email patterns.
        
        Args:
            email: The email address to validate
            
        Raises:
            CustomerError: If email doesn't match required format
                - Error type: INVALID_EMAIL
                - Details: Contains the invalid email
        """
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise CustomerError(
                message="Invalid email format",
                error_type="INVALID_EMAIL",
                details={"email": email}
            )

    @staticmethod
    def validate_password(password: str) -> None:
        """
        Validate password meets complexity requirements.
        
        Args:
            password: The password to validate
            
        Raises:
            CustomerError: If password doesn't meet requirements
                - Error type: INVALID_PASSWORD
                - Details: Contains password complexity requirements
        """
        if len(password) < 8:
            raise CustomerError(
                message="Password too short",
                error_type="INVALID_PASSWORD",
                details={"min_length": 8}
            )
        
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            raise CustomerError(
                message="Password does not meet complexity requirements", 
                error_type="INVALID_PASSWORD",
                details={
                    "requirements": [
                        "At least 8 characters",
                        "At least one uppercase letter",
                        "At least one lowercase letter", 
                        "At least one number",
                        "At least one special character (@$!%*?&)"
                    ]
                }
            )

class User(BaseUser):
    """
    General user model representing all user types in the system.
    
    Attributes:
        role: The user's role (defaults to CUSTOMER)
    """
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}
    role = Column(role_enum_type, default=RoleEnum.CUSTOMER)

    def __repr__(self):
        return f"User(username={self.username}, role={self.role})"

    def check_permission(self, required_role: RoleEnum) -> None:
        """
        Verify if user has the required role for an action.
        
        Args:
            required_role: Minimum role needed for the action
            
        Raises:
            PermissionError: If user doesn't have required role
        """
        if self.role != required_role:
            raise PermissionError(
                message=f"This action requires {required_role.value} role"
            )

class Customer(BaseUser):
    """
    Customer model representing end users of the system.
    
    Attributes:
        role: Always CUSTOMER
        addresses: List of associated shipping addresses
        ratings: Product ratings given by this customer
    """
    __tablename__ = "customer"
    __table_args__ = {'extend_existing': True}
    role = Column(role_enum_type, default=RoleEnum.CUSTOMER)
    addresses = relationship("Address", back_populates="customer", cascade="all, delete-orphan")
    ratings = relationship("models.good.ratings.ProductRating", back_populates="customer", cascade="all, delete-orphan", lazy="dynamic")
    
    def __repr__(self):
        return f"Customer(username={self.username})"

    def add_address(self, address) -> None:
        """
        Add a new shipping address for the customer.
        
        Args:
            address: Address object to add
            
        Raises:
            CustomerError: If maximum addresses (5) already exist
                - Error type: MAX_ADDRESSES_REACHED
                - Details: Current and max allowed address count
        """
        if len(self.addresses) >= 5:  #  limit
            raise CustomerError(
                message="Maximum number of addresses reached",
                error_type="MAX_ADDRESSES_REACHED",
                details={"current_count": len(self.addresses), "max_allowed": 5}
            )
        self.addresses.append(address)

    def remove_address(self, address_id: int) -> None:
        """
        Remove a shipping address by its ID.
        
        Args:
            address_id: ID of address to remove
            
        Raises:
            CustomerError: If address with given ID not found
                - Error type: ADDRESS_NOT_FOUND
                - Details: The requested address ID
        """
        address = next((addr for addr in self.addresses if addr.id == address_id), None)
        if not address:
            raise CustomerError(
                message="Address not found",
                error_type="ADDRESS_NOT_FOUND",
                details={"address_id": address_id}
            )
        self.addresses.remove(address)

class Manager(BaseUser):
    """
    Manager model representing shop managers in the system.
    
    Attributes:
        role: Always MANAGER
        shop_name: Name of the managed shop (unique)
        tenant_id: UUID identifying the shop/tenant
    """
    __tablename__ = "manager"
    __table_args__ = {'extend_existing': True}
    role = Column(role_enum_type, default=RoleEnum.MANAGER)
    shop_name = Column(String, unique=True, nullable=True)
    tenant_id = Column(UUID, nullable=False)
    
    def __repr__(self):
        return f"Manager(username={self.username}, tenant_id={self.tenant_id})"

class Admin(BaseUser):
    """
    Administrator model representing system administrators.
    
    Attributes:
        role: Always ADMIN
        tenant_id: UUID identifying the organization/tenant
    """
    __tablename__ = "admin"
    __table_args__ = {'extend_existing': True}
    role = Column(role_enum_type, default=RoleEnum.ADMIN)
    tenant_id = Column(UUID, nullable=False)
    
    def __repr__(self):
        return f"Admin(username={self.username}, tenant_id={self.tenant_id})"

class Invite(Base):
    """
    Invitation model for user registration.
    
    Attributes:
        token: Unique invitation token
        tenant_id: UUID of associated tenant/organization
    """
    __tablename__ = "invites"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    tenant_id = Column(UUID(as_uuid=True))