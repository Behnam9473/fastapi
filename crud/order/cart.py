from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from crud.base import CRUDBase
from models.inventory.inventory import Customization, Inventory
from models.order.cart import AnonymousCartTable, AuthenticatedCartTable, CartItemTable

class CRUDCart:
    """
    Provides CRUD operations for shopping carts, handling both authenticated and anonymous users.
    
    Attributes:
        None
    """
    def get_anonymous_cart(self, db: Session, session_id: UUID) -> Optional[AnonymousCartTable]:
        """
        Retrieve an anonymous user's shopping cart by their session ID.
        
        Args:
            db (Session): SQLAlchemy database session
            session_id (UUID): Unique session identifier for anonymous user
            
        Returns:
            Optional[AnonymousCartTable]: The anonymous cart if found, None otherwise
        """
        return db.query(AnonymousCartTable).filter(
            AnonymousCartTable.session_id == session_id
        ).first()

    def get_user_cart(self, db: Session, user_id: UUID) -> Optional[AuthenticatedCartTable]:
        """
        Retrieve an authenticated user's shopping cart by their user ID.
        
        Args:
            db (Session): SQLAlchemy database session
            user_id (UUID): Unique user identifier
            
        Returns:
            Optional[AuthenticatedCartTable]: The authenticated cart if found, None otherwise
        """
        return db.query(AuthenticatedCartTable).filter(
            AuthenticatedCartTable.user_id == user_id
        ).first()

    def create_anonymous_cart(self, db: Session, session_id: UUID) -> AnonymousCartTable:
        """
        Create a new shopping cart for an anonymous user.
        
        Args:
            db (Session): SQLAlchemy database session
            session_id (UUID): Unique session identifier for anonymous user
            
        Returns:
            AnonymousCartTable: The newly created anonymous cart
        """
        new_cart = AnonymousCartTable(
            items=[],
            session_id=session_id,
            total_items=0,
            total_price=0.0
        )
        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        return new_cart

    def create_user_cart(self, db: Session, user_id: UUID) -> AuthenticatedCartTable:
        """
        Create a new shopping cart for an authenticated user.
        
        Args:
            db (Session): SQLAlchemy database session
            user_id (UUID): Unique user identifier
            
        Returns:
            AuthenticatedCartTable: The newly created authenticated cart
        """
        new_cart = AuthenticatedCartTable(
            user_id=user_id,
            items=[],
            total_items=0,
            total_price=0.0
        )
        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        return new_cart
    
    def calcaulate_total_price(self, db: Session, product_id: int, quantity: int, customization_ids: list[int] = None) -> float:
        """
        Calculate the total price for a product including quantity and customizations.
        
        Args:
            db (Session): SQLAlchemy database session
            product_id (int): ID of the product
            quantity (int): Quantity of the product
            customization_ids (list[int], optional): List of customization IDs. Defaults to None.
            
        Returns:
            float: The calculated total price
            
        Raises:
            HTTPException: 404 if product not found
            HTTPException: 400 if product unavailable or invalid customizations
        """
        inventory = db.query(Inventory).filter(Inventory.id == product_id).first()
        if not inventory:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if not inventory.published:
            raise HTTPException(status_code=400, detail="Product is not available for sale")
            
        if inventory.qty < quantity:
            raise HTTPException(status_code=400, detail="Not enough quantity available")

        # Start with base sale price
        total_price = inventory.sale_price

        # Add customization prices if any
        if customization_ids:
            customizations = db.query(Customization).filter(
                Customization.id.in_(customization_ids),
                Customization.inv_id == product_id
            ).all()
            
            if len(customizations) != len(customization_ids):
                raise HTTPException(status_code=400, detail="Invalid customization IDs")
                
            # Add all customization prices
            for customization in customizations:
                if customization.prices:
                    total_price += sum(customization.prices)

        # Calculate final price with quantity
        final_price = total_price * quantity

        return final_price
    
    def add_item(self, db: Session, cart_id: UUID, product_id: int, quantity: int, total_price: float) -> CartItemTable:
        """
        Add an item to the shopping cart and update cart totals.
        
        Args:
            db (Session): SQLAlchemy database session
            cart_id (UUID): ID of the cart (anonymous or authenticated)
            product_id (int): ID of the product to add
            quantity (int): Quantity of the product
            total_price (float): Pre-calculated total price for the item
            
        Returns:
            CartItemTable: The newly created cart item
            
        Raises:
            HTTPException: 404 if cart not found
        """
        # Check cart type and get cart
        anon_cart = db.query(AnonymousCartTable).filter(
            AnonymousCartTable.cart_id == cart_id
        ).first()
        user_cart = db.query(AuthenticatedCartTable).filter(
            AuthenticatedCartTable.cart_id == cart_id
        ).first()
        
        cart = anon_cart or user_cart
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Create new cart item
        new_item = CartItemTable(
            cart_id=cart_id if isinstance(cart, AnonymousCartTable) else None,
            user_cart_id=cart_id if isinstance(cart, AuthenticatedCartTable) else None,
            product_id=product_id,
            quantity=quantity,
            price=total_price
        )
        db.add(new_item)

        # Update cart totals
        cart.total_items = quantity
        cart.total_price = total_price 
        
        # Update items field based on cart type
        if isinstance(cart, AnonymousCartTable):
            if not cart.items:
                cart.items = []
                cart.items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price": total_price
                })
        elif isinstance(cart, AuthenticatedCartTable):
            if not cart.items:
                cart.items = []
                cart.items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price": total_price
                })


        db.commit()
        db.refresh(new_item)
        return new_item

    def convert_to_authenticated(self, db: Session, session_id: UUID, user_id: UUID) -> AuthenticatedCartTable:
        """
        Convert an anonymous cart to an authenticated cart when user logs in.
        
        Args:
            db (Session): SQLAlchemy database session
            session_id (UUID): Anonymous session ID
            user_id (UUID): Authenticated user ID
            
        Returns:
            AuthenticatedCartTable: The new authenticated cart
            
        Raises:
            HTTPException: 404 if anonymous cart not found
        """
        # Get anonymous cart
        anon_cart = self.get_anonymous_cart(db, session_id)
        if not anon_cart:
            raise HTTPException(status_code=404, detail="Anonymous cart not found")

        # Create authenticated cart
        user_cart = AuthenticatedCartTable(
            user_id=user_id,
            items=anon_cart.items,
            total_items=anon_cart.total_items,
            total_price=anon_cart.total_price
        )
        db.add(user_cart)

        # Update cart items
        cart_items = db.query(CartItemTable).filter(
            CartItemTable.cart_id == anon_cart.cart_id
        ).all()
        
        for item in cart_items:
            item.cart_id = None
            item.user_cart_id = user_cart.cart_id

        # Delete anonymous cart
        db.delete(anon_cart)
        db.commit()
        db.refresh(user_cart)
        return user_cart

    def remove_item(self, db: Session, cart_id: UUID, item_id: int) -> bool:
        """
        Remove an item from the cart and update cart totals.
        
        Args:
            db (Session): SQLAlchemy database session
            cart_id (UUID): ID of the cart (anonymous or authenticated)
            item_id (int): ID of the item to remove
            
        Returns:
            bool: True if item was removed successfully, False otherwise
        """
        item = db.query(CartItemTable).filter(
            CartItemTable.id == item_id,
            (CartItemTable.cart_id == cart_id) | (CartItemTable.user_cart_id == cart_id)
        ).first()
        
        if not item:
            return False

        cart = (db.query(AnonymousCartTable).filter(AnonymousCartTable.cart_id == cart_id).first() or
                db.query(AuthenticatedCartTable).filter(AuthenticatedCartTable.cart_id == cart_id).first())
        
        if cart:
            cart.total_items -= item.quantity
            cart.total_price -= item.price * item.quantity
            cart.items = [i for i in cart.items if i["product_id"] != item.product_id]

        db.delete(item)
        db.commit()
        return True
    
    def get_items(self, db: Session, cart_id: UUID) -> List[CartItemTable]:
        """
        Retrieve all items in a cart with complete product details.
        
        Args:
            db (Session): SQLAlchemy database session
            cart_id (UUID): ID of the cart (anonymous or authenticated)
            
        Returns:
            List[CartItemTable]: List of cart items with product information
            
        Raises:
            HTTPException: 404 if cart not found or empty
        """
            # Get cart items with product details
        items = (
            db.query(CartItemTable, Inventory)
            .join(
                Inventory,
                CartItemTable.product_id == Inventory.id
            )
            .filter(
                (CartItemTable.cart_id == cart_id) | (CartItemTable.user_cart_id == cart_id)
            )
            .all()
        )
        
        if not items:
            raise HTTPException(status_code=404, detail="Cart not found or empty")

        # Transform the results to match CartItemResponse schema
        result = []
        for cart_item, product in items:
            item_dict = {
                "item_id": cart_item.item_id,
                "cart_id": cart_item.cart_id,
                "user_cart_id": cart_item.user_cart_id,
                "product_id": cart_item.product_id,
                "quantity": cart_item.quantity,
                "price": cart_item.price,
                "created_at": cart_item.created_at,
                "updated_at": cart_item.updated_at,
                "product": product
            }
            result.append(item_dict)
        return result



cart = CRUDCart()