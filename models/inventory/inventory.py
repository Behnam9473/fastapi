import uuid
from sqlalchemy import JSON, Boolean, Table, create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Enum, UUID 
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz
from database import Base

inventory_customization = Table(
    "inventory_customization",
    Base.metadata,
    Column("inventory_id", Integer, ForeignKey("inventory.id", ondelete="CASCADE"), primary_key=True),
    Column("customization_id", Integer, ForeignKey("customization.id", ondelete="CASCADE"), primary_key=True),
)

class Customization(Base):
    """
    Customization model represents product customization options.
    
    Attributes:
        id: Primary key
        name: Name of the customization option
        images: List of image URLs for this customization
        alternative_text: List of alternative texts for accessibility
        prices: List of prices for different customization options
        inv_id: Foreign key to Inventory
        inventories: Many-to-many relationship with Inventory
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    __tablename__ = "customization"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    images = Column(JSON, nullable=False, default=list)  # List of image URLs
    alternative_text = Column(JSON, nullable=False, default=list)  # List of alternative texts
    prices = Column(JSON, nullable=False, default=list)  # List of prices
    inv_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)  

    # Relationship to Good (many-to-many)
    inventories = relationship("Inventory", secondary="inventory_customization", back_populates="customizations")

    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

    __table_args__ = {'extend_existing': True}


class Inventory(Base):
    """
    Inventory model represents product inventory items.
    
    Attributes:
        id: Primary key
        good_id: Foreign key to Good table
        good: Relationship to Good model
        ratings: Relationship to ProductRating model
        seller_name: Name of the seller
        tenant_id: Tenant identifier
        purchase_price: Purchase price of the item
        sale_price: Selling price of the item
        file: AR file path or URL
        qty: Available quantity
        published: Whether item is published for sale
        customizations: Many-to-many relationship with Customization
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to Good table
    good_id = Column(Integer, ForeignKey("good.id", ondelete="CASCADE"), nullable=False)
    good = relationship("models.good.goods.Good", back_populates="inventories")
    ratings = relationship("models.good.ratings.ProductRating", back_populates="inventory", cascade="all, delete-orphan")

    # Seller information fetched from Manager/Admin (determined by tenant_id)
    seller_name = Column(String, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), unique=False)
    purchase_price = Column(Float, nullable=False)  # قیمت خرید
    sale_price = Column(Float, nullable=False)  # قیمت فروش
    file = Column(String, nullable=True)  # AR (File path or URL)
    qty = Column(Integer, nullable=False)  # Quantity
    published = Column(Boolean, default=False)  # انتشار (if available for sale)

    # Relationship to Customization (many-to-many)
    customizations = relationship("Customization", secondary=inventory_customization, back_populates="inventories")

    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))
    __table_args__ = {'extend_existing': True}
    