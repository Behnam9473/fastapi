# services/schedulers/visit_archiver.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import logging
from services.redis.visit_tracker import VisitTracker, get_visit_tracker
from services.schedulers.tasks import archive_visit_data

logger = logging.getLogger(__name__)

async def archive_visit_data_task(visit_tracker: VisitTracker = Depends(get_visit_tracker),
                                db: AsyncSession = Depends(get_db)):
    """Trigger the Celery task to archive visit data"""
    try:
        # Launch the celery task
        task = archive_visit_data.delay()
        return {
            "message": "Visit data archiving scheduled",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Error scheduling archive task: {e}")
        return {
            "message": "Failed to schedule archiving task",
            "error": str(e)
        }