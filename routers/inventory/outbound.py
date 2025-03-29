# Standard library imports
import uuid
from datetime import datetime

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Models
from models.inventory.inventory import Inventory
from models.good.goods import Good
from models.users.users import Manager, Admin

# Schemas
from schemas.inventory.outbound import (
    OutboundCreate,
    OutboundResponse,
    OutboundUpdate
)

# Utils
from utils.auth import get_current_manager

router = APIRouter(prefix="", tags=["Inventory"])


def get_tenant_and_manager(current_user: dict, db: Session):
    """Helper function to get tenant_id and manager based on user role"""
    if current_user["role"] == "MANAGER":
        manager = db.query(Manager).filter(Manager.id == current_user["user_id"]).first()
        if not manager:
            raise HTTPException(status_code=400, detail="Manager not found.")
        current_user["tenant_id"] = manager.tenant_id
        manager = db.query(Manager).filter(Manager.tenant_id == current_user["tenant_id"]).first()

    if current_user["role"] == "ADMIN":
        manager = db.query(Admin).filter(Admin.id == current_user["user_id"]).first()
        if not manager:
            raise HTTPException(status_code=400, detail="Manager not found.")
        current_user["tenant_id"] = manager.tenant_id
        manager = db.query(Admin).filter(Admin.tenant_id == current_user["tenant_id"]).first()
    
    return manager, current_user["tenant_id"]

@router.post("/outbound", response_model=OutboundResponse)
def create_outbound(
    outbound_data: OutboundCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_manager)
):
    """
    Creates a new Outbound record for a Good (reduces inventory).
    Only MANAGER or ADMIN can create this record.
    """
    if current_user["role"] not in ["MANAGER", "ADMIN", "SUPERUSER"]:
        raise HTTPException(status_code=403, detail="Not authorized to add outbound records.")

    # Check if the good exists
    good = db.query(Good).filter(Good.id == outbound_data.good_id).first()
    if not good:
        raise HTTPException(status_code=400, detail="Good does not exist.")

    manager, tenant_id = get_tenant_and_manager(current_user, db)
    if not manager:
        raise HTTPException(status_code=400, detail="Manager not found for this Organization.")

    # Find matching inventory record
    inventory_record = db.query(Inventory).filter(
        Inventory.good_id == outbound_data.good_id,
        Inventory.tenant_id == tenant_id,
        Inventory.purchase_price == outbound_data.purchase_price,
        Inventory.sale_price == outbound_data.sale_price
    ).first()

    if not inventory_record:
        raise HTTPException(status_code=404, detail="No matching inventory record found.")

    if inventory_record.qty < outbound_data.qty:
        raise HTTPException(status_code=400, detail="Insufficient quantity in inventory.")

    # Update inventory quantity
    inventory_record.qty -= outbound_data.qty

    # If quantity becomes 0, remove the record
    if inventory_record.qty == 0:
        db.delete(inventory_record)
    
    db.commit()
    
    # Create response object
    response = OutboundResponse(
        id=inventory_record.id,
        good=good,
        seller_name=manager.username,
        purchase_price=outbound_data.purchase_price,
        sale_price=outbound_data.sale_price,
        qty=outbound_data.qty,
        file=outbound_data.file,
        published=outbound_data.published,
        created_at=datetime.now()
    )
    
    return response

