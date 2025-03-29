# Standard library imports
from typing import List, Optional, Dict
from datetime import date, timedelta, datetime

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Database imports
from database import get_db

# Service layer imports
from services.redis.visit_tracker import VisitTracker, get_visit_tracker
from services.schedulers.tasks import archive_visit_data
from services.schedulers.visit_archiver import archive_visit_data_task

# Model imports
from models.stats.stats import ProductVisitHistory, ProductVisitDetails

# Authentication imports
from utils.auth import get_current_manager

# Schema imports
from schemas.visit.visit import (
    VisitMetrics,
    ArchiveTaskResponse, 
    ArchiveTaskStatus,
    TopProductVisit,
    ProductDailySummary,
    VisitDetail
)

router = APIRouter(
    prefix="/stats/visits",
    tags=["Visit Statistics"],
    dependencies=[Depends(get_current_manager)]  # Require manager authentication
)
@router.get("/redis/metrics/all", response_model=Dict[str, VisitMetrics])
async def get_all_products_metrics(
    visit_tracker: VisitTracker = Depends(get_visit_tracker)
):
    """
    Get visit metrics for all products that have recorded visits in Redis.
    
    Returns:
        Dict[str, dict]: Dictionary with product IDs as keys and their metrics as values.
        Each metric contains:
            - total_visits: Total number of visits
            - unique_visits: Number of unique visitors
            - user_visits: Number of authenticated user visits
    """
    metrics = visit_tracker.get_all_product_metrics()
    
    # Convert product_id keys to strings for JSON compatibility
    return {str(product_id): metrics for product_id, metrics in metrics.items()}



@router.post("/archive", response_model=ArchiveTaskResponse)
async def trigger_archive(
    visit_tracker: VisitTracker = Depends(get_visit_tracker)
):
    """
    Manually trigger the archiving process to move Redis data to the database.
    
    This endpoint initiates a background task that:
    1. Retrieves visit data from Redis
    2. Stores it in the permanent database
    3. Clears the Redis cache
    
    Returns:
        dict: Contains task ID and status URL for tracking the archive process
        
    Raises:
        500: If archiving task fails to schedule
    """
    try:
        # Start the archiving task without waiting
        task = archive_visit_data.delay()
        
        return {
            "message": "Archive task scheduled successfully",
            "task_id": str(task.id),
            "status_url": f"/stats/visits/archive/status/{task.id}",
            "status": "pending"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule archive task: {str(e)}"
        )

@router.get("/archive/status/{task_id}", response_model=ArchiveTaskStatus)
async def get_archive_status(task_id: str):
    """
    Get the status of an archive task.
    
    Parameters:
        task_id (str): The ID of the archive task to check
        
    Returns:
        dict: Current status of the archive task including:
            - status: Task status (pending/completed/failed)
            - result: Task result if completed
            - error: Error message if failed
    """
    try:
        task = archive_visit_data.AsyncResult(task_id)
        
        if task.ready():
            result = task.get()
            return {
                "task_id": task_id,
                "status": result["status"],
                "result": result,
                "completed": True
            }
        else:
            return {
                "task_id": task_id,
                "status": "pending",
                "completed": False
            }
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e),
            "completed": True
        }

@router.get("/redis/top-products", response_model=List[TopProductVisit])
async def get_top_visited_products(
    limit: int = 10,
    visit_tracker: VisitTracker = Depends(get_visit_tracker)
):
    """
    Retrieve the most visited products from Redis (real-time data).
    
    Parameters:
        limit (int, optional): Number of top products to return. Default is 10.
    
    Returns:
        List[dict]: List of products with their visit counts, ordered by visits (descending)
    """
    return visit_tracker.get_top_visited_products(limit)

@router.get("/redis/metrics/{product_id}", response_model=VisitMetrics)
async def get_current_metrics(
    product_id: int,
    visit_tracker: VisitTracker = Depends(get_visit_tracker)
):
    """
    Get real-time visit metrics for a specific product from Redis.
    
    Parameters:
        product_id (int): ID of the product to get metrics for
    
    Returns:
        VisitMetrics: Object containing total_visits, unique_visits, and other metrics
        
    Raises:
        404: If no metrics found for the specified product
    """
    metrics = visit_tracker.get_visit_metrics(product_id)
    if metrics is None:
        raise HTTPException(
            status_code=404,
            detail=f"No visit metrics found for product {product_id}"
        )
    return metrics

@router.post("/archive/manual", response_model=ArchiveTaskResponse)
async def manual_archive_with_date_range(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    visit_tracker: VisitTracker = Depends(get_visit_tracker),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger the archiving process with optional date range parameters.
    
    Parameters:
        start_date (date, optional): Start date for archiving data
        end_date (date, optional): End date for archiving data
        
    Returns:
        ArchiveTaskResponse: Contains task information and status
    """
    try:
        # Get current metrics before archiving
        pre_archive_metrics = visit_tracker.get_all_product_metrics()
        
        # Start the archiving task
        task = archive_visit_data.delay()
        
        return {
            "message": "Manual archive task scheduled successfully",
            "task_id": str(task.id),
            "status_url": f"/stats/visits/archive/status/{task.id}",
            "status": "pending",
            "pre_archive_metrics": {
                "total_products": len(pre_archive_metrics),
                "total_visits": sum(m['total_visits'] for m in pre_archive_metrics.values()),
                "total_unique_visits": sum(m['unique_visits'] for m in pre_archive_metrics.values())
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule manual archive task: {str(e)}"
        )

# ... existing imports and code ...

@router.get("/history/summary", response_model=List[ProductDailySummary])
async def get_visit_history(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    product_ids: Optional[List[int]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve historical visit data from the database.
    
    Parameters:
        start_date (date, optional): Filter data from this date
        end_date (date, optional): Filter data until this date
        product_ids (List[int], optional): Filter specific product IDs
        
    Returns:
        List[ProductDailySummary]: Historical visit data grouped by product and date
    """
    try:
        query = select(ProductVisitHistory)
        
        # Apply date filters if provided
        if start_date:
            query = query.where(ProductVisitHistory.visit_date >= start_date)
        if end_date:
            query = query.where(ProductVisitHistory.visit_date <= end_date)
        if product_ids:
            query = query.where(ProductVisitHistory.product_id.in_(product_ids))
            
        # Order by product_id and date for consistent results
        query = query.order_by(
            ProductVisitHistory.product_id,
            ProductVisitHistory.visit_date
        )
        
        result = db.execute(query)
        history_records = result.scalars().all()
        
        # Group records by product_id
        product_summaries = {}
        for record in history_records:
            if record.product_id not in product_summaries:
                product_summaries[record.product_id] = {
                    "product_id": record.product_id,
                    "daily_stats": []
                }
            
            product_summaries[record.product_id]["daily_stats"].append({
                "date": record.visit_date,
                "total_visits": record.total_visits,
                "unique_visits": record.unique_visits
            })
        
        return list(product_summaries.values())
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve visit history: {str(e)}"
        )

@router.get("/history/details/{product_id}", response_model=List[VisitDetail])
async def get_visit_details(
    product_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve detailed visit records for a specific product.
    
    Parameters:
        product_id (int): Product ID to get details for
        start_date (datetime, optional): Filter from this timestamp
        end_date (datetime, optional): Filter until this timestamp
        limit (int): Maximum number of records to return (default: 100)
        
    Returns:
        List[VisitDetail]: Detailed visit records
    """
    try:
        query = select(ProductVisitDetails).where(
            ProductVisitDetails.product_id == product_id
        )
        
        if start_date:
            query = query.where(ProductVisitDetails.visit_timestamp >= start_date)
        if end_date:
            query = query.where(ProductVisitDetails.visit_timestamp <= end_date)
            
        query = query.order_by(ProductVisitDetails.visit_timestamp.desc())
        query = query.limit(limit)
        
        result = db.execute(query)
        details = result.scalars().all()
        
        return [
            VisitDetail(
                client_ip=detail.client_ip,
                timestamp=detail.visit_timestamp,
                user_agent=detail.user_agent,
                referrer=detail.referrer,
                session_id=detail.session_id,
                user_id=detail.user_id
            ) for detail in details
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve visit details: {str(e)}"
        )
