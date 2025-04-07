from datetime import datetime, timedelta, timezone
import uuid
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.users.users import Admin, Invite, Manager
from schemas.users.manager import AdminCreate, ManagerCreate, ManagerUpdate
from utils.auth import get_password_hash, create_access_token, verify_access_token

class ManagerRepository:
    """
    Repository class for managing Manager and Admin user operations.
    
    Args:
        db (Session): SQLAlchemy database session
    """
    def __init__(self, db: Session):
        """Initialize the repository with a database session."""
        self.db = db

    def create_manager(self, user: ManagerCreate) -> Manager:
        """
        Create a new manager with tenant ID.
        
        Args:
            user (ManagerCreate): Manager creation data
            
        Returns:
            Manager: The created manager object
            
        Raises:
            HTTPException: If email is already registered (400 status code)
        """
        if self._get_manager_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(user.password)
        tenant_uuid = uuid.uuid4()
        
        new_user = Manager(
            username=user.username,
            email=user.email,
            shop_name=user.shop_name,
            hashed_password=hashed_password,
            role="MANAGER",
            tenant_id=tenant_uuid,
        )
        return self._save(new_user)

    def create_admin(self, user: AdminCreate, invite_token: Optional[str] = None) -> Admin:
        """
        Create a new admin user.
        
        Args:
            user (AdminCreate): Admin creation data
            invite_token (Optional[str]): Optional invite token for tenant association
            
        Returns:
            Admin: The created admin object
            
        Raises:
            HTTPException: If email/username is already registered (400 status code)
                          or if invite token is invalid (400 status code)
        """
        existing_user = self.db.query(Admin).filter(
            or_(Admin.email == user.email, Admin.username == user.username)
        ).first()
        
        if existing_user:
            detail = "Email already registered" if existing_user.email == user.email else "Username already registered"
            raise HTTPException(status_code=400, detail=detail)

        tenant_id = uuid.uuid4()
        if invite_token:
            token_data = verify_access_token(invite_token)
            if not token_data:
                raise HTTPException(status_code=400, detail="Invalid or expired invite token")
            tenant_id = uuid.UUID(token_data["tenant_id"])

        new_admin = Admin(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password),
            role=user.role,
            tenant_id=tenant_id,
        )
        return self._save(new_admin)

    def get_manager(self, user_id: int, username: str) -> Manager:
        """
        Retrieve a manager by ID and username.
        
        Args:
            user_id (int): Manager's ID
            username (str): Manager's username
            
        Returns:
            Manager: The manager object if found, None otherwise
        """
        return self.db.query(Manager).filter(
            Manager.username == username,
            Manager.id == user_id,
        ).first()

    def get_admin(self, user_id: int, username: str) -> Admin:
        """
        Retrieve an admin by ID and username.
        
        Args:
            user_id (int): Admin's ID
            username (str): Admin's username
            
        Returns:
            Admin: The admin object if found, None otherwise
        """
        return self.db.query(Admin).filter(
            Admin.username == username,
            Admin.id == user_id,
        ).first()

    def get_tenant_admins(self, tenant_id: uuid.UUID) -> List[Admin]:
        """
        Retrieve all admins belonging to a specific tenant.
        
        Args:
            tenant_id (uuid.UUID): Tenant's unique identifier
            
        Returns:
            List[Admin]: List of admin objects for the tenant
        """
        return self.db.query(Admin).filter(Admin.tenant_id == tenant_id).all()

    def update_manager(self, manager_id: int, update_data: ManagerUpdate) -> Manager:
        """
        Update manager information.
        
        Args:
            manager_id (int): Manager's ID
            update_data (ManagerUpdate): Data to update
            
        Returns:
            Manager: The updated manager object
            
        Raises:
            HTTPException: If manager is not found (404 status code)
        """
        manager = self.db.query(Manager).filter(Manager.id == manager_id).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(manager, field, value)
        
        self.db.commit()
        self.db.refresh(manager)
        return manager

    def create_invite(self, manager: Manager) -> str:
        """
        Create an invitation link for admin registration.
        
        Args:
            manager (Manager): Manager creating the invite
            
        Returns:
            str: The generated invite URL
            
        Raises:
            HTTPException: If manager is not found (404 status code)
                          or if user is not a manager (403 status code)
        """
        if not manager:
            raise HTTPException(status_code=404, detail="User not found")
        
        if manager.role.value != "MANAGER":
            raise HTTPException(status_code=403, detail="Only managers can create invite links")

        token_data = {
            "tenant_id": str(manager.tenant_id),
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
            "sub": str(manager.username),
            "role": str(manager.role),
            "id": int(manager.id)
        }
        
        token = create_access_token(token_data)
        invite_link = f"http://127.0.0.1:8000/users/register?invite_token={token}"

        invite = Invite(token=token, tenant_id=manager.tenant_id)
        self._save(invite)

        return invite_link

    def _get_manager_by_email(self, email: str) -> Optional[Manager]:
        """
        Internal method to retrieve a manager by email.
        
        Args:
            email (str): Manager's email
            
        Returns:
            Optional[Manager]: The manager object if found, None otherwise
        """
        return self.db.query(Manager).filter(Manager.email == email).first()

    def _save(self, model: any) -> any:
        """
        Internal method to save and refresh a model.
        
        Args:
            model (any): SQLAlchemy model to save
            
        Returns:
            any: The saved and refreshed model
        """
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model