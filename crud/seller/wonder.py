from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from models.seller.wonders import Wonders
from models.inventory.inventory import Inventory
from schemas.seller.wonders import WondersCreate, WondersRead

def create_wonder(db: Session, wonder: WondersCreate, tenant_id: int) -> Wonders:
    """
    Create a new wonder in the database.
    
    Args:
        db: Database session
        wonder: Wonder creation schema
        tenant_id: ID of the tenant creating the wonder
        
    Returns:
        Created wonder object
    """
    # Retrieve the inventory item to access its sale_price
    inventory_item = db.query(Inventory).filter(Inventory.id == wonder.inventory_id).first()
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Calculate the special_price based on the inventory's sale_price and percent_off
    sale_price = inventory_item.sale_price
    special_price = sale_price - (sale_price * wonder.percent_off / 100)

    db_wonder = Wonders(
        inventory_id=wonder.inventory_id,
        tenant_id=tenant_id,
        title=wonder.title,
        description=wonder.description,
        is_active=wonder.is_active,
        percent_off=wonder.percent_off,
        special_price=special_price,
        start_date=wonder.start_date,
        end_date=wonder.end_date,
        created_at=datetime.now(datetime.timezone.utc),
        updated_at=datetime.now(datetime.timezone.utc),
    )
    
    db.add(db_wonder)
    db.commit()
    db.refresh(db_wonder)
    return db_wonder

def get_wonder(db: Session, wonder_id: int, tenant_id: int) -> Optional[Wonders]:
    """
    Get a wonder by ID for a specific tenant.
    
    Args:
        db: Database session
        wonder_id: ID of the wonder to retrieve
        tenant_id: ID of the tenant
        
    Returns:
        Wonder object if found, None otherwise
    """
    return db.query(Wonders).filter(
        Wonders.id == wonder_id,
        Wonders.tenant_id == tenant_id
    ).first()

def get_wonders(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[Wonders]:
    """
    Get all wonders for a specific tenant with optional filtering.
    
    Args:
        db: Database session
        tenant_id: ID of the tenant
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, only return active wonders
        
    Returns:
        List of wonder objects
    """
    query = db.query(Wonders).filter(Wonders.tenant_id == tenant_id)
    
    if active_only:
        query = query.filter(Wonders.is_active == True)
        
    return query.offset(skip).limit(limit).all()

def update_wonder(
    db: Session,
    wonder_id: int,
    tenant_id: int,
    wonder_update: WondersCreate
) -> Optional[Wonders]:
    """
    Update a wonder in the database.
    
    Args:
        db: Database session
        wonder_id: ID of the wonder to update
        tenant_id: ID of the tenant
        wonder_update: Updated wonder data
        
    Returns:
        Updated wonder object if found, None otherwise
    """
    db_wonder = get_wonder(db, wonder_id, tenant_id)
    if not db_wonder:
        return None

    # If inventory_id is being updated, recalculate special_price
    if wonder_update.inventory_id != db_wonder.inventory_id:
        inventory_item = db.query(Inventory).filter(Inventory.id == wonder_update.inventory_id).first()
        if not inventory_item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        sale_price = inventory_item.sale_price
        special_price = sale_price - (sale_price * wonder_update.percent_off / 100)
    else:
        special_price = db_wonder.special_price

    # Update wonder attributes
    for key, value in wonder_update.dict().items():
        setattr(db_wonder, key, value)
    
    db_wonder.special_price = special_price
    db_wonder.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_wonder)
    return db_wonder

def delete_wonder(db: Session, wonder_id: int, tenant_id: int) -> bool:
    """
    Delete a wonder from the database.
    
    Args:
        db: Database session
        wonder_id: ID of the wonder to delete
        tenant_id: ID of the tenant
        
    Returns:
        True if wonder was deleted, False otherwise
    """
    db_wonder = get_wonder(db, wonder_id, tenant_id)
    if not db_wonder:
        return False
        
    db.delete(db_wonder)
    db.commit()
    return True

def toggle_wonder_status(db: Session, wonder_id: int, tenant_id: int) -> Optional[Wonders]:
    """
    Toggle the active status of a wonder.
    
    Args:
        db: Database session
        wonder_id: ID of the wonder to toggle
        tenant_id: ID of the tenant
        
    Returns:
        Updated wonder object if found, None otherwise
    """
    db_wonder = get_wonder(db, wonder_id, tenant_id)
    if not db_wonder:
        return None
        
    db_wonder.is_active = not db_wonder.is_active
    db_wonder.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_wonder)
    return db_wonder
