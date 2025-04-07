# Standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

# Local application imports
# Database
from database import get_db

# Models
from models.inventory.inventory import Inventory
from models.seller.wonders import Wonders

# Schemas
from schemas.seller.wonders import WondersRead

# Services
from services.redis.rate_limit import rate_limit
from services.redis.visit_tracker import VisitTracker, get_visit_tracker

router = APIRouter(prefix="/store", tags=["Store"])

@router.get("/wonders", response_model=WondersRead)
async def get_all_wonders(db: Session = Depends(get_db), _ = Depends(rate_limit)):
    """
    Retrieve all wonder items (special offers/discounts)
    
    Returns:
        List[dict]: A list of wonder items with their details including:
            - id: Unique identifier for the wonder item
            - inventory_id: Related inventory item ID
            - tenant_id: Tenant/organization ID
            - title: Display title of the wonder item
            - description: Detailed description
            - is_active: Whether the offer is currently active
            - percent_off: Discount percentage (0-100)
            - special_price: Special discounted price
            - start_date: When the offer becomes active
            - end_date: When the offer expires
    
    Raises:
        HTTPException: 500 if any database error occurs
    """
    try:
        # Query for all wonder items
        query = select(Wonders)
        result = db.execute(query).scalars().all()
        
        # Convert wonder items to list of dictionaries
        wonder_items = []
        for item in result:
            wonder_items.append({
                "id": item.id,
                "inventory_id": item.inventory_id,
                "tenant_id": item.tenant_id,
                "title": item.title,
                "description": item.description,
                "is_active": item.is_active,
                "percent_off": item.percent_off,
                "special_price": item.special_price,
                "start_date": item.start_date,
                "end_date": item.end_date
            })
        
        return wonder_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[dict])
async def get_published_inventory(db: Session = Depends(get_db), _ = Depends(rate_limit)):
    """
    Retrieve all published inventory items
    
    Returns:
        List[dict]: A list of published inventory items with:
            - id: Unique inventory item ID
            - seller_name: Name of the seller
            - sale_price: Current selling price
            - qty: Available quantity
            - file: Associated file/image
            - good_id: Related good ID
    
    Raises:
        HTTPException: 500 if any database error occurs
    """
    try:
        # Query for published inventory items
        query = select(Inventory).where(Inventory.published == True)
        result = db.execute(query).scalars().all()
        
        # Convert inventory items to list of dictionaries
        inventory_items = []
        for item in result:
            inventory_items.append({
                "id": item.id,
                "seller_name": item.seller_name,
                "sale_price": item.sale_price,
                "qty": item.qty,
                "file": item.file,
                "good_id": item.good_id
            })
        
        return inventory_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{good_id}", response_model=List[dict])
async def get_inventory_by_good_id(
    good_id: int,
    request: Request,
    db: Session = Depends(get_db),
    visit_tracker: VisitTracker = Depends(get_visit_tracker),
    _ = Depends(rate_limit),
):
    """
    Retrieve inventory items by good_id and track visits
    
    Args:
        good_id (int): The ID of the good to retrieve inventory for
        request (Request): FastAPI request object for getting client info
        
    Returns:
        List[dict]: Inventory items with same good_id including:
            - id: Inventory item ID
            - seller_name: Seller name
            - sale_price: Current price
            - qty: Available quantity
            - file: Associated file/image
            - good_id: Good ID
            - viewer_user_id: ID of authenticated viewer (if any)
    
    Notes:
        - Tracks each visit to this endpoint for analytics
        - Requires valid Authorization header for user tracking
    
    Raises:
        HTTPException: 500 if any database error occurs
    """
    try:
        # Track the visit - extract token from authorization header
        client_ip = request.client.host
        token = None
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                user_info = await get_current_user(token)
                user_id = user_info["user_id"]
            except:
                pass
        
        await visit_tracker.track_visit(good_id, client_ip, token)

        # Query for inventory items by good_id
        query = select(Inventory).where(Inventory.good_id == good_id)
        result = db.execute(query).scalars().all()
        
        # Convert inventory items to list of dictionaries
        inventory_items = []
        for item in result:
            item_dict = {
                "id": item.id,
                "seller_name": item.seller_name,
                "sale_price": item.sale_price,
                "qty": item.qty,
                "file": item.file,
                "good_id": item.good_id,
                "viewer_user_id": user_id  # Include the user_id of the viewer
            }
            inventory_items.append(item_dict)
        
        return inventory_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category/{category_id}", response_model=List[dict])
async def get_inventory_by_category(category_id: int, db: Session = Depends(get_db), _ = Depends(rate_limit)):
    """
    Retrieve inventory items by category ID
    
    Args:
        category_id (int): The category ID to filter inventory by
        
    Returns:
        List[dict]: Inventory items belonging to specified category with:
            - id: Inventory item ID
            - seller_name: Seller name
            - sale_price: Current price
            - qty: Available quantity
            - file: Associated file/image
            - good_id: Good ID
    
    Raises:
        HTTPException: 500 if any database error occurs
    """
    try:
        # Query for inventory items where the associated good belongs to the specified category
        query = (select(Inventory)
                .join(Inventory.good)
                .where(Inventory.good.has(category_id=category_id)))
        result = db.execute(query).scalars().all()
        
        # Convert inventory items to list of dictionaries
        inventory_items = []
        for item in result:
            inventory_items.append({
                "id": item.id,
                "seller_name": item.seller_name,
                "sale_price": item.sale_price,
                "qty": item.qty,
                "file": item.file,
                "good_id": item.good_id
            })
        
        return inventory_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/seller/{seller_name}", response_model=List[dict],)
async def get_inventory_by_seller(seller_name: str, db: Session = Depends(get_db),_ = Depends(rate_limit)):
    """
    Retrieve inventory items by seller name
    
    Args:
        seller_name (str): Exact name of the seller to filter by
        
    Returns:
        List[dict]: Inventory items from specified seller with:
            - id: Inventory item ID
            - seller_name: Seller name
            - sale_price: Current price
            - qty: Available quantity
            - file: Associated file/image
            - good_id: Good ID
    
    Raises:
        HTTPException: 500 if any database error occurs
    """
    try:
        # Query for inventory items by seller name
        query = select(Inventory).where(Inventory.seller_name == seller_name)
        result = db.execute(query).scalars().all()
        
        # Convert inventory items to list of dictionaries
        inventory_items = []
        for item in result:
            inventory_items.append({
                "id": item.id,
                "seller_name": item.seller_name,
                "sale_price": item.sale_price,
                "qty": item.qty,
                "file": item.file,
                "good_id": item.good_id
            })
        
        return inventory_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/wonders", response_model=List[dict])
async def get_all_wonders(db: Session = Depends(get_db), _ = Depends(rate_limit)):
    """
    Retrieve all wonder items
    """
    try:
        # Query for all wonder items
        query = select(Wonders)
        result = db.execute(query).scalars().all()
        
        # Convert wonder items to list of dictionaries
        wonder_items = []
        for item in result:
            wonder_items.append({
                "id": item.id,
                "inventory_id": item.inventory_id,
                "tenant_id": item.tenant_id,
                "title": item.title,
                "description": item.description,
                "is_active": item.is_active,
                "percent_off": item.percent_off,
                "special_price": item.special_price,
                "start_date": item.start_date,
                "end_date": item.end_date
            })
        
        return wonder_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wonders/{wonder_id}", response_model=dict)
async def get_wonder_by_id(wonder_id: int, db: Session = Depends(get_db), _ = Depends(rate_limit)):
    """
    Retrieve a specific wonder item by ID
    
    Args:
        wonder_id (int): The unique ID of the wonder item to retrieve
        
    Returns:
        dict: Wonder item details including:
            - id: Unique identifier
            - inventory_id: Related inventory item ID
            - tenant_id: Tenant/organization ID
            - title: Display title
            - description: Detailed description
            - is_active: Whether active
            - percent_off: Discount percentage
            - special_price: Special price
            - start_date: Activation date
            - end_date: Expiration date
    
    Raises:
        HTTPException: 404 if wonder not found
        HTTPException: 500 if any database error occurs
    """
    try:
        query = select(Wonders).where(Wonders.id == wonder_id)
        result = db.execute(query).scalar_one_or_none()
        
        if not result:
            raise HTTPException(status_code=404, detail="Wonder not found")
            
        return {
            "id": result.id,
            "inventory_id": result.inventory_id,
            "tenant_id": result.tenant_id,
            "title": result.title,
            "description": result.description,
            "is_active": result.is_active,
            "percent_off": result.percent_off,
            "special_price": result.special_price,
            "start_date": result.start_date,
            "end_date": result.end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

