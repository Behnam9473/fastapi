from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import pytz

class ProductRating(Base):
    """
    Represents a product rating in the system.
    
    Attributes:
        id (int): Primary key identifier for the rating.
        customer_id (int): Foreign key to the customer who created the rating.
        inventory_id (int): Foreign key to the inventory item being rated.
        rating (float): Numeric rating value between 1 and 5.
        comment (str, optional): Optional text comment about the rating.
        created_at (DateTime): UTC timestamp when the rating was created.
        updated_at (DateTime): UTC timestamp when the rating was last updated.
        
    Relationships:
        customer: Reference to the Customer model (many-to-one).
        inventory: Reference to the Inventory model (many-to-one).
        
    Constraints:
        - Rating value must be between 1 and 5 (inclusive).
    """
    __tablename__ = "product_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id", ondelete="CASCADE"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    customer = relationship("models.users.users.Customer", back_populates="ratings", lazy="joined")
    inventory = relationship("models.inventory.inventory.Inventory", back_populates="ratings", lazy="joined")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        {'extend_existing': True}
    )