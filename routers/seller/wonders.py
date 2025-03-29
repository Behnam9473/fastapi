# Standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Models
from models.users.users import Manager, Admin

# Schemas
from schemas.seller.wonders import WondersCreate, WondersRead

# Authentication
from utils.auth import get_current_manager

# CRUD operations
from crud.seller.wonder import (
    create_wonder as crud_create_wonder,
    get_wonder as crud_get_wonder,
    get_wonders as crud_get_wonders,
    update_wonder as crud_update_wonder,
    delete_wonder as crud_delete_wonder,
    toggle_wonder_status as crud_toggle_wonder_status
)

router = APIRouter(prefix="/inventory/wonders", tags=["Wonders"])

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

@router.post("/", response_model=WondersRead)
def create_wonder(wonder: WondersCreate, current_user: dict = Depends(get_current_manager), db: Session = Depends(get_db)):
    if current_user["role"] not in ["ADMIN", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Not authorized to create wonders")

    _, tenant_id = get_tenant_and_manager(current_user, db)
    return crud_create_wonder(db, wonder, tenant_id)

@router.get("/{wonder_id}", response_model=WondersRead)
def read_wonder(wonder_id: int, current_user: dict = Depends(get_current_manager), db: Session = Depends(get_db)):
    _, tenant_id = get_tenant_and_manager(current_user, db)
    wonder = crud_get_wonder(db, wonder_id, tenant_id)
    if not wonder:
        raise HTTPException(status_code=404, detail="Wonder not found")
    return wonder

@router.get("/", response_model=List[WondersRead])
def read_wonders(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: dict = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    _, tenant_id = get_tenant_and_manager(current_user, db)
    return crud_get_wonders(db, tenant_id, skip, limit, active_only)

@router.put("/{wonder_id}", response_model=WondersRead)
def update_wonder(
    wonder_id: int,
    wonder: WondersCreate,
    current_user: dict = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    _, tenant_id = get_tenant_and_manager(current_user, db)
    updated_wonder = crud_update_wonder(db, wonder_id, tenant_id, wonder)
    if not updated_wonder:
        raise HTTPException(status_code=404, detail="Wonder not found")
    return updated_wonder

@router.delete("/{wonder_id}")
def delete_wonder(wonder_id: int, current_user: dict = Depends(get_current_manager), db: Session = Depends(get_db)):
    _, tenant_id = get_tenant_and_manager(current_user, db)
    if not crud_delete_wonder(db, wonder_id, tenant_id):
        raise HTTPException(status_code=404, detail="Wonder not found")
    return {"message": "Wonder deleted successfully"}

@router.patch("/{wonder_id}/toggle", response_model=WondersRead)
def toggle_wonder(wonder_id: int, current_user: dict = Depends(get_current_manager), db: Session = Depends(get_db)):
    _, tenant_id = get_tenant_and_manager(current_user, db)
    toggled_wonder = crud_toggle_wonder_status(db, wonder_id, tenant_id)
    if not toggled_wonder:
        raise HTTPException(status_code=404, detail="Wonder not found")
    return toggled_wonder