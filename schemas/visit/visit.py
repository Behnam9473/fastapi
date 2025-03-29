# app/models/visit_models.py
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, date

class VisitMetrics(BaseModel):
    # product_id: int
    total_visits: int
    unique_visits: int
    user_visits: int = 0  # Number of visits from authenticated users

class VisitDetail(BaseModel):
    client_ip: str
    timestamp: datetime
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[int] = None

class TopProductVisit(BaseModel):
    product_id: int
    total_visits: int
    unique_visits: int
    user_visits: int

class ArchiveTaskResponse(BaseModel):
    message: str
    task_id: str
    status_url: str
    status: str

class ArchiveTaskStatus(BaseModel):
    task_id: str
    status: str
    completed: bool
    result: Optional[Dict] = None
    error: Optional[str] = None

class DailyVisitStats(BaseModel):
    date: date
    total_visits: int
    unique_visits: int

class ProductDailySummary(BaseModel):
    product_id: int
    daily_stats: List[DailyVisitStats]

class ProductTotalStats(BaseModel):
    product_id: int
    total_visits: int
    unique_visits: int
    days_tracked: int


class PreArchiveMetrics(BaseModel):
    total_products: int
    total_visits: int
    total_unique_visits: int

class ArchiveTaskResponse(BaseModel):
    message: str
    task_id: str
    status_url: str
    status: str
    pre_archive_metrics: Optional[PreArchiveMetrics] = None