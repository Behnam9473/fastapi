from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from crud.base import CRUDBase
from models.good.goods import Good
from models.inventory.inventory import Inventory, Customization
from schemas.inventory.inbound import InboundCreate, InboundUpdate, CustomizationCreate
from datetime import datetime
from sqlalchemy.orm import joinedload

class CRUDInventory(CRUDBase[Inventory, InboundCreate, InboundUpdate]):
    # Customization related methods
    def create_customization(self, db: Session, *, inv_id: int, obj_in: CustomizationCreate) -> Customization:
        """Create a new customization for a specific good."""
        # Check if inventory exists
        inventory = db.query(self.model).filter(self.model.id == inv_id).first()
        if not inventory:
            raise HTTPException(status_code=404, detail="good not found")
            
        customization = Customization(**obj_in.model_dump())
        customization.inv_id = inv_id
        db.add(customization)
        db.commit()
        db.refresh(customization)
        return customization

    def get(self, db: Session, id: int) -> Optional[Inventory]:
        """Get an inventory item by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, *, tenant_id: UUID) -> List[Inventory]:
        """Get all inventory items for a tenant."""
        return db.query(self.model).filter(self.model.tenant_id == tenant_id).all()

    def create(self, db: Session, *, obj_in: InboundCreate, tenant_id: UUID, seller_name: str) -> Inventory:
        """Create a new inventory item."""
        # Check if similar inventory record exists
        existing_inbound = db.query(self.model).filter(
            self.model.good_id == obj_in.good_id,
            self.model.tenant_id == tenant_id,
            self.model.purchase_price == obj_in.purchase_price,
            self.model.sale_price == obj_in.sale_price
        ).first()

        if existing_inbound:
            # Update existing record
            existing_inbound.qty += obj_in.qty
            existing_inbound.file = obj_in.file
            existing_inbound.published = obj_in.published
            db.commit()
            db.refresh(existing_inbound)
            return existing_inbound

        # Create new record if no existing match
        db_obj = Inventory(
            good_id=obj_in.good_id,
            seller_name=seller_name,
            purchase_price=obj_in.purchase_price,
            sale_price=obj_in.sale_price,
            tenant_id=tenant_id,
            file=obj_in.file,
            qty=obj_in.qty,
            created_at=datetime.now(),
            published=obj_in.published
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Inventory, obj_in: InboundUpdate) -> Inventory:
        """Update an inventory item."""
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_tenant(self, db: Session, *, tenant_id: UUID) -> List[Inventory]:
        """Get all inventory items for a specific tenant."""
        return db.query(self.model).filter(self.model.tenant_id == tenant_id).all()



    def get_customizations(self, db: Session, *, inv_id: int, skip: int = 0, limit: int = 100) -> List[Customization]:
        """Get customizations for a specific good."""
        return db.query(Customization).filter(Customization.inv_id == inv_id).offset(skip).limit(limit).all()

    def get_customization(self, db: Session, *, inv_id: int, id: int) -> Optional[Customization]:
        """Get a specific customization."""
        return db.query(Customization).filter(
            Customization.inv_id == inv_id,
            Customization.id == id
        ).first()

    def update_customization(self, db: Session, *, db_obj: Customization, obj_in: CustomizationCreate) -> Customization:
        """Update a customization."""
        update_data = obj_in.model_dump()
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_customization(self, db: Session, *, id: int) -> Customization:
        """Remove a customization."""
        obj = db.query(Customization).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def delete(self, db: Session, *, id: int) -> Inventory:
        """Delete an inventory item."""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return 
    


    def _load_customizations(self, db: Session, inbounds: List[Inventory]) -> None:
        """Helper function to load customizations for inbounds."""
        inbound_ids = [inbound.id for inbound in inbounds]
        customizations = db.query(Customization)\
            .filter(Customization.inv_id.in_(inbound_ids))\
            .all()
        
        customizations_by_id = {custom.inv_id: [] for custom in customizations}
        for custom in customizations:
            customizations_by_id[custom.inv_id].append(custom)
        
        for inbound in inbounds:
            inbound.customizations = customizations_by_id.get(inbound.id, [])

    def get_inbounds(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Inventory]:
        """Get all inbound records with their customizations."""
        inbounds = db.query(self.model)\
            .options(joinedload(self.model.customizations))\
            .offset(skip).limit(limit)\
            .all()
        
        self._load_customizations(db, inbounds)
        return inbounds

    def get_inbound(self, db: Session, *, id: int) -> Optional[Inventory]:
        """Get a specific inbound record with its customizations."""
        inbound = db.query(self.model)\
            .options(joinedload(self.model.customizations))\
            .filter(self.model.id == id)\
            .first()
        
        if inbound:
            self._load_customizations(db, [inbound])
        
        return inbound


    def create_inbound(self, db: Session, *, obj_in: InboundCreate, seller_name) -> Inventory:
        """Create a new inbound record or update existing one."""
        # Check if good exists and is approved
        good = db.query(Good).filter(Good.id == obj_in.good_id).first()
        if not good:
            raise HTTPException(status_code=404, detail="Good not found")
        
        if good.status == "pending" or not good.sku:
            raise HTTPException(
                status_code=400, 
                detail="Cannot create inbound for goods with pending status or missing SKU"
            )

        # Check if similar inventory record exists  
        existing_inbound = db.query(self.model).filter(
            self.model.good_id == obj_in.good_id,
            self.model.seller_name == seller_name, 
            self.model.purchase_price == obj_in.purchase_price,
            self.model.sale_price == obj_in.sale_price
        ).first()

        if existing_inbound:
            # Update existing record's quantity
            existing_inbound.qty += obj_in.qty
            db.commit()
            db.refresh(existing_inbound)
            return existing_inbound

        # Create new record if no existing match
        db_obj = self.model(**obj_in.model_dump())
        db_obj.seller_name = seller_name
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_inbound(self, db: Session, *, db_obj: Inventory, obj_in: InboundUpdate) -> Inventory:
        """Update an inbound record."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
inventory = CRUDInventory(Inventory)