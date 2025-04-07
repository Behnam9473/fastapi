"""
Cart Router Module

This module handles all cart-related operations including:
- Creating anonymous carts for guest users
- Creating authenticated carts for logged-in customers
- Adding items to carts
- Retrieving cart items
- Converting anonymous carts to authenticated carts

Routes:
- POST /anonymous - Create anonymous cart
- POST /user - Create authenticated cart for customer
- POST /items/{cart_id} - Add item to cart
- GET /items/{cart_id} - Get cart items
- PUT /convert/{session_id} - Convert anonymous cart to authenticated
"""

# Standard library imports
import uuid

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Models
from models.inventory.inventory import Customization, Inventory
from models.order.cart import CartItemTable

# Schemas
from schemas.order.cart import (
    AnonymousCart,
    AuthenticatedCart,
    CartItem,
    CartItemResponse
)

# Utils and CRUD
from utils.auth import get_current_user
from crud.order.cart import cart  # Import the CRUDCart instance

router = APIRouter(
    prefix="/carts",
    tags=["carts"]
)

def generate_session_id():
    """
    Generate a unique session ID using UUID4.
    
    Returns:
        UUID: A randomly generated UUID4 object
    """
    return uuid.uuid4()

@router.post("/anonymous", response_model=AnonymousCart)
def create_anonymous_cart(db: Session = Depends(get_db)):
    """
    Create a new anonymous cart for guest users.
    
    Args:
        db (Session): Database session dependency
        
    Returns:
        AnonymousCart: Newly created anonymous cart object
    """
    session_id = generate_session_id()
    return cart.create_anonymous_cart(db, session_id = session_id)

@router.post("/user", response_model=AuthenticatedCart)
async def create_user_cart(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new authenticated cart for logged-in customers.
    
    Args:
        db (Session): Database session dependency
        current_user (dict): Current authenticated user information
        
    Returns:
        AuthenticatedCart: Newly created authenticated cart object
        
    Raises:
        HTTPException: If user is not a customer or already has a cart
    """
    if current_user.get("role") != "CUSTOMER":
        raise HTTPException(
            status_code=403,
            detail="Only customers can create carts"
        )
    
    user_id = current_user.get("user_id")
    if cart.get_user_cart(db, user_id):
        raise HTTPException(status_code=400, detail="User already has a cart")
    
    return cart.create_user_cart(db, user_id)

@router.post("/items/{cart_id}", response_model=CartItem)
async def add_item_to_cart(
    cart_id: uuid.UUID,
    product_id: int,
    quantity: int,
    customization_ids: list[int] = None,
    db: Session = Depends(get_db)
):
    """
    Add an item to an existing cart.
    
    Args:
        cart_id (UUID): ID of the cart to add item to
        product_id (int): ID of the product to add
        quantity (int): Quantity of the product to add
        customization_ids (list[int], optional): List of customization IDs
        db (Session): Database session dependency
        
    Returns:
        CartItem: Added cart item details
    """
    final_price = cart.calcaulate_total_price(db, product_id, quantity, customization_ids)

    return cart.add_item(db, cart_id, product_id, quantity, final_price)

@router.get("/items/{cart_id}", response_model=list[CartItemResponse])
async def get_cart_items(
    cart_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve all items from a specific cart.
    
    Args:
        cart_id (UUID): ID of the cart to get items from
        db (Session): Database session dependency
        
    Returns:
        list[CartItemResponse]: List of cart items with their details
    """
    result = cart.get_items(db, cart_id)
    return result

@router.put("/convert/{session_id}")
async def convert_anonymous_to_authenticated(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Convert an anonymous cart to an authenticated cart.
    
    Args:
        session_id (UUID): Session ID of the anonymous cart
        db (Session): Database session dependency
        current_user (dict): Current authenticated user information
        
    Returns:
        dict: Success message and new cart ID
        
    Raises:
        HTTPException: If user is not a customer or already has a cart
    """
    if current_user.get("role") != "CUSTOMER":
        raise HTTPException(
            status_code=403, 
            detail="Only customers can convert carts"
        )

    user_id = current_user.get("user_id")
    if cart.get_user_cart(db, user_id):
        raise HTTPException(status_code=400, detail="User already has a cart")

    user_cart = cart.convert_to_authenticated(db, session_id, user_id)
    return {"message": "Cart converted successfully", "new_cart_id": str(user_cart.cart_id)}
