import pytz
from sqlalchemy import Column, UUID, ForeignKey, String, JSON, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime, timedelta
from database import Base


class AnonymousCartTable(Base):
    """
    Represents an anonymous user's shopping cart in the database.
    
    Attributes:
        cart_id (UUID): Primary key, automatically generated UUID.
        session_id (UUID): Unique session identifier for anonymous users.
        items (JSON): List of cart items stored as JSON.
        total_items (Integer): Total count of items in cart.
        total_price (Float): Total price of all items in cart.
        created_at (DateTime): When the cart was created (UTC).
        expires_at (DateTime): When the cart expires (1 day after creation).
        updated_at (DateTime): When the cart was last updated (UTC).
    """
    __tablename__ = "anonymous_carts"

    cart_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID, unique=True, nullable=False)  # Unique session identifier
    items = Column(JSON, default=[])  # Stores cart items as JSON
    total_items = Column(Integer, default=0)
    total_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC) + timedelta(days=1))  # Expiry time for TTL policy (1 day)
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

    def __repr__(self):
        """
        Returns a string representation of the cart object.
        
        Returns:
            str: String representation showing cart_id and key attributes.
        """
        return f"<AnonymousCart(cart_id={self.cart_id}, session_id={self.session_id}, total_items={self.total_items})>"


class AuthenticatedCartTable(Base):
    """
    Represents an authenticated user's shopping cart in the database.
    
    Attributes:
        cart_id (UUID): Primary key, automatically generated UUID.
        user_id (Integer): Foreign key linking to customer.id.
        items (JSON): List of cart items stored as JSON.
        total_items (Integer): Total count of items in cart.
        total_price (Float): Total price of all items in cart.
        created_at (DateTime): When the cart was created (UTC).
        updated_at (DateTime): When the cart was last updated (UTC).
    """
    __tablename__ = "authenticated_carts"

    cart_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('customer.id'), nullable=False)  # Link to user
    items = Column(JSON, default=[])  # Stores cart items as JSON
    total_items = Column(Integer, default=0)
    total_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

    def __repr__(self):
        """
        Returns a string representation of the cart object.
        
        Returns:
            str: String representation showing cart_id and key attributes.
        """
        return f"<AuthenticatedCart(cart_id={self.cart_id}, user_id={self.user_id}, total_items={self.total_items})>"


class CartItemTable(Base):
    """
    Represents an item in a shopping cart (either anonymous or authenticated).
    
    Attributes:
        item_id (Integer): Primary key for the cart item.
        cart_id (UUID): Foreign key to anonymous_carts.cart_id (nullable).
        user_cart_id (UUID): Foreign key to authenticated_carts.cart_id (nullable).
        product_id (Integer): Identifier for the product.
        quantity (Integer): Quantity of this product in cart (default 1).
        price (Float): Price of the product.
        created_at (DateTime): When the item was added to cart (UTC).
        updated_at (DateTime): When the item was last updated (UTC).
    """
    __tablename__ = "cart_items"

    item_id = Column(Integer, primary_key=True)
    cart_id = Column(UUID, ForeignKey('anonymous_carts.cart_id'), nullable=True)  # Reference to anonymous cart
    user_cart_id = Column(UUID, ForeignKey('authenticated_carts.cart_id'), nullable=True)  # Reference to authenticated cart
    product_id = Column(Integer, nullable=False)  # Product identifier
    quantity = Column(Integer, default=1)  # Quantity of the product
    price = Column(Float, nullable=False)  # Price of the product
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

    def __repr__(self):
        """
        Returns a string representation of the cart object.
        
        Returns:
            str: String representation showing cart_id and key attributes.
        """
        return f"<CartItem(item_id={self.item_id}, cart_id={self.cart_id}, user_cart_id={self.user_cart_id}, product_id={self.product_id}, quantity={self.quantity})>"
