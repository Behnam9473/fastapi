import uuid
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz
from database import Base

class Wonders(Base):
    """
    Represents a 'Wonder' deal in the system.
    
    Wonders are special deals or discounts that sellers can create for their inventory items.
    Each wonder is linked to a specific inventory item and seller (tenant).
    """
    __tablename__ = "wonders"
    id = Column(Integer, primary_key=True, index=True)
    """Primary key identifier for the wonder."""
    
    # Foreign key to Inventory table
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    """Foreign key reference to the inventory item this wonder applies to."""
    inventory = relationship("Inventory")
    """SQLAlchemy relationship to the associated Inventory object."""
    
    # Link to tenant (seller)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    """UUID identifier of the seller (tenant) who created this wonder."""
    
    # Wonder specific fields
    title = Column(String, nullable=True)
    """Title/name of the wonder deal."""
    description = Column(String, nullable=True)
    """Detailed description of the wonder deal."""
    is_active = Column(Boolean, default=True)
    """Flag indicating if this wonder is currently active."""
    percent_off = Column(Float, nullable=False)
    """Percentage discount offered by this wonder (0-100)."""
    special_price = Column(Float, nullable=False)
    """Fixed special price offered by this wonder."""
    
    # Timestamps
    start_date = Column(DateTime, nullable=False)
    """Date/time when this wonder deal becomes active (UTC)."""
    end_date = Column(DateTime, nullable=True)
    """Optional date/time when this wonder deal expires (UTC)."""
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    """Timestamp of when this wonder was created (UTC)."""
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))
    """Timestamp of when this wonder was last updated (UTC)."""

    __table_args__ = {'extend_existing': True}
    """Allows extending an existing table definition if it already exists."""