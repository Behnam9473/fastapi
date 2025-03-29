from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import pytz

class ProductRating(Base):
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