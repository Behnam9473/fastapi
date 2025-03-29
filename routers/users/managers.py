# Python standard library imports
from datetime import datetime, timedelta, timezone
from typing import List
import uuid

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Repository
from crud.users.managers import ManagerRepository

# Schemas
from schemas.users.manager import (
    AdminCreate,
    AdminRead,
    ManagerCreate,
    ManagerResponse,
    ManagerUpdate
)

# Authentication utilities
from utils.auth import (
    create_access_token,
    get_current_manager,
    get_password_hash,
    verify_access_token,
)

# Exception handling
from utils.exceptions import (
    AuthenticationError,
    NotFoundError,
    PermissionError
)

router = APIRouter(prefix="/managers", tags=["Managers"])

@router.post("/sellers", response_model=ManagerResponse)
def create_user(user: ManagerCreate, db: Session = Depends(get_db)):
    """Create a new manager (seller) account."""
    manager_repo = ManagerRepository(db)
    return manager_repo.create_manager(user)

@router.post("/admin_register", response_model=AdminRead)
def create_admin(
    user: AdminCreate,
    db: Session = Depends(get_db),
    invite_token: str = Query(None)
):
    """Register a new admin user."""
    manager_repo = ManagerRepository(db)
    return manager_repo.create_admin(user, invite_token)

@router.get("/me", response_model=ManagerResponse)
def read_manager_me(
    current_user: dict = Depends(get_current_manager), 
    db: Session = Depends(get_db)
):
    """Get the current manager's profile."""
    manager_repo = ManagerRepository(db)
    return manager_repo.get_manager(
        user_id=current_user.get("user_id"),
        username=current_user.get("username")
    )

@router.get("/admin/me", response_model=ManagerResponse)
def read_admin_me(
    current_user: dict = Depends(get_current_manager), 
    db: Session = Depends(get_db)
):
    """Get the current admin's profile."""
    if current_user.get("role") != "ADMIN":
        raise PermissionError("Only ADMIN can View its own profile information")
    manager_repo = ManagerRepository(db)
    return manager_repo.get_admin(
        user_id=current_user.get("user_id"),
        username=current_user.get("username")
    )

@router.get("/admins", response_model=List[AdminRead])
def get_users(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_manager)
):
    """Get all admins for the current manager's tenant."""
    manager_repo = ManagerRepository(db)
    manager = manager_repo.get_manager(
        user_id=current_user.get("user_id"),
        username=current_user.get("username"),

    )
    role = current_user.get("role")

    if role != "MANAGER":
        raise PermissionError("Only managers can view Admins")     
    return manager_repo.get_tenant_admins(manager.tenant_id)

@router.patch("/update", response_model=ManagerResponse)
def partial_update_manager(
    user_update: ManagerUpdate,
    current_user: dict = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """Partially update Stor's profile information."""
    if current_user.get("role") != "MANAGER":
        raise PermissionError("Only managers can update profile information")
        
    manager_repo = ManagerRepository(db)
    return manager_repo.update_manager(
        manager_id=current_user["user_id"],
        update_data=user_update
    )
@router.post("/invite", response_model=str)
def create_invite_link(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_manager)
):
    """Create an invitation link for new admin registration."""
    manager_repo = ManagerRepository(db)
    manager = manager_repo.get_manager(
        user_id=current_user.get("user_id"),
        username=current_user.get("username")
    )
    return manager_repo.create_invite(manager)