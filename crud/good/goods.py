"""
CRUD operations for Goods management.

This module provides CRUD (Create, Read, Update, Delete) operations for Goods,
including validation and relationship management with categories and colors.

Key Features:
- Create goods with validation for categories, colors and images
- Paginated retrieval of goods
- Filtering by category, color and tenant
- Validation and status management for goods
"""
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from crud.base import CRUDBase
from crud.good.category import CategoryCRUD
from models.good.goods import Good, Category, generate_sku
from models.good.colors import Color
from schemas.good.goods import GoodCreate, GoodUpdate
# from services.save_images import save_images
class CRUDGood(CRUDBase[Good, GoodCreate, GoodUpdate]):
    """
    CRUD operations for Goods with extended functionality.
    
    Inherits from CRUDBase and adds:
    - Validation during creation and update
    - Relationship management with categories and colors
    - Status and validation workflows
    """
    
    def get(self, db: Session, id: int) -> Optional[Good]:
        """
        Retrieve a single good by its ID.
        
        Args:
            db: Database session
            id: ID of the good to retrieve
            
        Returns:
            Optional[Good]: The good object if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[Good]:
        """
        Retrieve multiple goods with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List[Good]: List of good objects
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: GoodCreate, tenant_id: UUID) -> Good:
        """
        Create a new good with validation.
        
        Args:
            db: Database session
            obj_in: Good creation schema
            tenant_id: UUID of the tenant creating the good
            
        Returns:
            Good: The newly created good
            
        Raises:
            HTTPException: If validation fails for category, colors or images
        """
        return self.validate_and_create(db=db, obj_in=obj_in, tenant_id=tenant_id)
        
    def validate_and_create(self, db: Session, *, obj_in: GoodCreate, tenant_id: UUID) -> Good:
        """
        Validate and create a new good with its relationships.
        
        Performs comprehensive validation including:
        - Category existence and hierarchy
        - Color existence
        - Image requirements
        
        Args:
            db: Database session
            obj_in: Good creation schema
            tenant_id: UUID of the tenant creating the good
            
        Returns:
            Good: The newly created good
            
        Raises:
            HTTPException: If validation fails for category, colors or images
        """
        # Validate category and its hierarchy
        category = db.query(Category).filter(Category.id == obj_in.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category does not exist.")
        
        # Fetch the full category hierarchy
        crud = CategoryCRUD(db)
        category_hierarchy = crud.get_hierarchy(obj_in.category_id)
        
        # Validate colors
        if not obj_in.colors or len(obj_in.colors) == 0:
            raise HTTPException(status_code=400, detail="At least one color is required.")
        
        colors = db.query(Color).filter(Color.id.in_(obj_in.colors)).all()
        if len(colors) != len(obj_in.colors):
            raise HTTPException(status_code=400, detail="One or more colors do not exist.")

        # Validate images
        if not obj_in.images or len(obj_in.images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required.")

        # Create the Good with relationships
        new_good = Good(
            name=obj_in.name,
            description=obj_in.description,
            weight=obj_in.weight,
            length=obj_in.length,
            height=obj_in.height,
            category_id=obj_in.category_id,
            colors=colors,  # Many-to-many relationship
            tenant_id=tenant_id
        )

        # Save images and get their paths
        saved_image_paths = obj_in.images
        new_good.images = saved_image_paths

        db.add(new_good)
        db.commit()
        db.refresh(new_good)

        return new_good


    def update(self, db: Session, *, id: int, obj_in: GoodUpdate) -> Optional[Good]:
        """
        Update an existing good with validation.
        
        Args:
            db: Database session
            id: ID of the good to update
            obj_in: Good update schema
            
        Returns:
            Optional[Good]: The updated good if found, None otherwise
            
        Raises:
            HTTPException: If validation fails for category, colors or images
        """
        db_obj = self.get(db, id=id)
        if not db_obj:
            return None

        # Validate category if provided
        if obj_in.category_id is not None:
            category = db.query(Category).filter(Category.id == obj_in.category_id).first()
            if not category:
                raise HTTPException(status_code=400, detail="Category does not exist.")

        # Validate colors if provided
        if obj_in.colors is not None:
            if len(obj_in.colors) == 0:
                raise HTTPException(status_code=400, detail="At least one color is required.")
            colors = db.query(Color).filter(Color.id.in_(obj_in.colors)).all()
            if len(colors) != len(obj_in.colors):
                raise HTTPException(status_code=400, detail="One or more colors do not exist.")
            db_obj.colors = colors

        # Validate images if provided
        if obj_in.images is not None and len(obj_in.images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required.")

        # Update other fields
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            if field != 'colors':  # Skip colors as we handled them above
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: int) -> Optional[Good]:
        """
        Delete a good by ID.
        
        Args:
            db: Database session
            id: ID of the good to delete
            
        Returns:
            Optional[Good]: The deleted good if found, None otherwise
        """
        db_obj = self.get(db, id=id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj


    def get_by_category(
        self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Good]:
        """
        Retrieve goods filtered by category ID with pagination.
        
        Args:
            db: Database session
            category_id: ID of the category to filter by
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List[Good]: List of goods in the specified category
        """
        return (
            db.query(self.model)
            .filter(self.model.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_color(
        self, db: Session, *, color_id: int, skip: int = 0, limit: int = 100
    ) -> List[Good]:
        """
        Retrieve goods filtered by color ID with pagination.
        
        Args:
            db: Database session
            color_id: ID of the color to filter by
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List[Good]: List of goods with the specified color
        """
        return (
            db.query(self.model)
            .filter(self.model.colors.any(id=color_id))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def my_goods(self, db: Session, *, tenant_id: UUID) -> List[Good]:
        """
        Retrieve all goods belonging to a specific tenant.
        
        Args:
            db: Database session
            tenant_id: UUID of the tenant
            
        Returns:
            List[Good]: List of goods belonging to the tenant
        """

        return db.query(self.model).filter(self.model.tenant_id == tenant_id).all()
    
    def get_superuser_validated_goods(self, db: Session) -> List[Good]:
        """
        Retrieve all goods that have been validated by a superuser.
        
        Args:
            db: Database session
            
        Returns:
            List[Good]: List of validated goods
        """
        return db.query(self.model).filter(self.model.is_validated == True).all()
    
    def get_pending_goods(self, db: Session) -> List[Good]:
        """
        Retrieve all goods with 'pending' status.
        
        Args:
            db: Database session
            
        Returns:
            List[Good]: List of pending goods
        """
        return db.query(self.model).filter(self.model.status == "pending").all()
    
    def validate(self, db: Session, *, id: int) -> Optional[Good]:
        """
        Validate a good and generate its SKU if approved.
        
        Args:
            db: Database session
            id: ID of the good to validate
            
        Returns:
            Optional[Good]: The validated good if found, None otherwise
        """
        db_obj = self.get(db, id=id)
        if db_obj:
            db_obj.is_validated = True
            db_obj.update_status()
            # Generate and set SKU when good is validated
            if db_obj.status == "approved" and not db_obj.sku:
                db_obj.sku = generate_sku(db_obj)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def invalidate(self, db: Session, *, id: int, superuser_description: str) -> Optional[Good]:
        """
        Invalidate a good with a superuser description.
        
        Args:
            db: Database session
            id: ID of the good to invalidate
            superuser_description: Reason for invalidation
            
        Returns:
            Optional[Good]: The invalidated good if found, None otherwise
        """
        db_obj = self.get(db, id=id)
        if db_obj:
            db_obj.is_validated = False
            db_obj.superuser_description = superuser_description
            db_obj.update_status()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

good = CRUDGood(Good)


