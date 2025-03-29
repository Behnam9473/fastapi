

# Python standard library imports
from typing import List
import uuid

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# Local application imports
from database import get_db
from models.users.users import Customer
from schemas.users.customers import CustomerCreate, CustomerResponse
from schemas.users.users import UserResponse
from utils.auth import *

router = APIRouter(prefix="/customer", tags=["Customer"])



@router.post("/register", response_model=CustomerResponse)
def create_user(
    user: CustomerCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new customer.
    
    This endpoint creates a new customer account with the provided details.
    It ensures email uniqueness and handles password hashing.
    
    Args:
        user (CustomerCreate): Customer registration data including:
            - username: Customer's username
            - email: Customer's email address
            - password: Customer's plain text password
        db (Session): Database session dependency
        
    Returns:
        CustomerResponse: Created customer data (excluding sensitive information)
        
    Raises:
        HTTPException: 400 if email is already registered
        
    Security:
        - Passwords are hashed before storage
        - Email addresses must be unique
        - Role is automatically set to "CUSTOMER"
    """
    if db.query(Customer).filter(Customer.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")



    hashed_password = get_password_hash(user.password)
    new_user = Customer(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="CUSTOMER",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/me", response_model=CustomerResponse)
def read_user_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db),):
    """
    Get the current customer's profile.
    
    This endpoint retrieves the profile information of the currently authenticated customer.
    
    Args:
        current_user (dict): Current authenticated user
    
    Returns:
        UserResponse: Profile information of the current customer
    """

       # Query to retrieve customer information

    username = current_user.get("username")
    user_id = current_user.get("user_id")
    customer_info = db.query(Customer).filter(
        Customer.username == username,
        Customer.id == user_id,
    ).first()

    return customer_info

