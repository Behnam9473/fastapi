import uuid
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz
from database import Base

class Wonders(Base):
    __tablename__ = "wonders"
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to Inventory table
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    inventory = relationship("Inventory")
    
    # Link to tenant (seller)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Wonder specific fields
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    percent_off = Column(Float, nullable=False)  # Optional percentage off for wonder
    special_price = Column(Float, nullable=False)  # Optional special price for wonder
    
    # Timestamps
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

    __table_args__ = {'extend_existing': True}