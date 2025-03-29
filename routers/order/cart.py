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
    return uuid.uuid4()

@router.post("/anonymous", response_model=AnonymousCart)
def create_anonymous_cart(db: Session = Depends(get_db)):
    session_id = generate_session_id()
    return cart.create_anonymous_cart(db, session_id = session_id)

@router.post("/user", response_model=AuthenticatedCart)
async def create_user_cart(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
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
    final_price = cart.calcaulate_total_price(db, product_id, quantity, customization_ids)

    return cart.add_item(db, cart_id, product_id, quantity, final_price)

@router.get("/items/{cart_id}", response_model=list[CartItemResponse])
async def get_cart_items(
    cart_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    result = cart.get_items(db, cart_id)
    return result

@router.put("/convert/{session_id}")
async def convert_anonymous_to_authenticated(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
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
