"""
Authentication Router Module

This module handles all authentication-related routes in the ZOHOOR-AR application.
It provides endpoints for user and seller authentication using OAuth2 password flow.

Features:
- Regular user authentication
- Seller (manager/admin) authentication
- JWT token generation
- Role-based access control
"""

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Schema definitions
from schemas.auth import TokenResponse

# Authentication utilities
from utils.auth import create_access_token

# CRUD operations
from crud.auth import get_authenticator

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate regular users and generate an access token.
    
    This endpoint validates user credentials and generates a JWT token
    for authenticated users.
    
    Args:
        request (OAuth2PasswordRequestForm): Form containing username and password
        db (Session): Database session dependency
        
    Returns:
        TokenResponse: JWT access token and token type
        
    Raises:
        HTTPException: 400 error if credentials are invalid
        
    Example:
        Form Data:
            username: user@example.com
            password: userpassword
    """
    authenticator = get_authenticator("user")
    user = authenticator.authenticate(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(
        data={"sub": str(user.username), "role": user.role.value, "id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/sellerlogin", response_model=TokenResponse)
def seller_login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate sellers (managers and admins) and generate an access token.
    
    This endpoint attempts to authenticate the user first as a manager,
    then as an admin if manager authentication fails.
    
    Args:
        request (OAuth2PasswordRequestForm): Form containing username and password
        db (Session): Database session dependency
        
    Returns:
        TokenResponse: JWT access token and token type
        
    Raises:
        HTTPException: 400 error if credentials are invalid
        
    Example:
        Form Data:
            username: admin@example.com
            password: adminpassword
            
    Note:
        This endpoint tries manager authentication first, then falls back to
        admin authentication if manager authentication fails.
    """
    # Try manager authentication first, then admin if that fails
    authenticator = get_authenticator("manager")
    user = authenticator.authenticate(db, request.username, request.password)
    
    if not user:
        authenticator = get_authenticator("admin")
        user = authenticator.authenticate(db, request.username, request.password)
        
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    tenant_id = str(user.tenant_id)
    access_token = create_access_token(
        data={"sub": str(user.username), "role": user.role.value, "id": user.id, "tenant_id": tenant_id}
    )
    return {"access_token": access_token, "token_type": "bearer"}