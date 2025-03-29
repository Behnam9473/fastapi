from services.schedulers.celery_app import celery_app
from services.redis.visit_tracker import get_visit_tracker
from database import db
from models.stats.stats import ProductVisitHistory, ProductVisitDetails  
import logging
from datetime import datetime, date
import asyncio

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, time_limit=300)
def archive_visit_data(self):
    """Celery task to archive Redis visit data to database"""
    try:
        with db.get_session() as session:
            visit_tracker = get_visit_tracker()
            self.update_state(state='STARTED', meta={'status': 'Processing'})
            
            # Get all product visit data from Redis
            all_products = visit_tracker.get_all_product_metrics()
            today = date.today()
            
            archived_products = 0
            archived_details = 0
            failed_products = []
            
            for product_id, metrics in all_products.items():
                try:
                    # Create history record using VisitMetrics schema
                    history = ProductVisitHistory(
                        product_id=product_id,
                        visit_date=today,
                        total_visits=metrics['total_visits'],
                        unique_visits=metrics['unique_visits'],
                        user_visits=metrics['user_visits'],
                        created_at=datetime.utcnow()
                    )
                    session.add(history)
                    
                    # Get visitor details for this product
                    visitor_keys = list(visit_tracker.redis.scan_iter(
                        match=f"product:{product_id}:visitor:*"
                    ))
                    
                    # Process each visitor's details
                    for visitor_key in visitor_keys:
                        visitor_data = visit_tracker.redis.hgetall(visitor_key)
                        if not visitor_data:
                            continue
                            
                        # Convert bytes to string if necessary
                        visitor_data = {
                            k.decode() if isinstance(k, bytes) else k: 
                            v.decode() if isinstance(v, bytes) else v 
                            for k, v in visitor_data.items()
                        }
                        
                        # Create visit detail record
                        visit_detail = ProductVisitDetails(
                            product_id=product_id,
                            client_ip=visitor_data.get('client_ip', ''),
                            visit_timestamp=datetime.fromisoformat(visitor_data.get('timestamp', datetime.utcnow().isoformat())),
                            user_agent=visitor_data.get('user_agent'),
                            referrer=visitor_data.get('referrer'),
                            session_id=visitor_data.get('session_id'),
                            user_id=int(visitor_data.get('user_id', 0)) or None,
                            created_at=datetime.utcnow()
                        )
                        session.add(visit_detail)
                        archived_details += 1
                    
                    # Commit after each product to avoid large transactions
                    session.commit()
                    archived_products += 1
                    
                    # Clear Redis data for this product after successful commit
                    visit_tracker.clear_visit_data(product_id)
                    
                except Exception as e:
                    logger.error(f"Error processing product {product_id}: {e}")
                    session.rollback()
                    failed_products.append(product_id)
                    continue
            
            return {
                "status": "completed",
                "products_archived": archived_products,
                "details_archived": archived_details,
                "failed_products": failed_products,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in archive task: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }