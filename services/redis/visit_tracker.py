# app/services/visit_tracker.py
from datetime import timedelta, date, datetime
from typing import Dict, Optional, List
from redis import Redis
from redis.exceptions import RedisError
from schemas.visit.visit import VisitMetrics
from .redis_client import get_redis_client
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.stats.stats import ProductVisitHistory, ProductVisitDetails
from database import get_db
import logging
from utils.auth import get_current_user  # Add this import at the top

logger = logging.getLogger(__name__)

class VisitTracker:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.expiry_days = 1  # Centralized configuration

    def _get_keys(self, product_id: int, client_ip: str = None) -> tuple:
        """Generate consistent Redis keys for a product"""
        return (
            f"product:{product_id}:total_visits",
            f"product:{product_id}:unique_visits",
            f"product:{product_id}:visitor:{client_ip}"
        )

    async def track_visit(self, product_id: int, client_ip: str, token: Optional[str] = None) -> bool:
        """Track a product visit, returns success status"""
        total_visits_key, unique_visits_key, visitor_detail_key = self._get_keys(product_id)
        user_visits_key = f"product:{product_id}:user_visits"
        visitor_detail_key = f"product:{product_id}:visitor:{client_ip}"

        try:
            pipe = self.redis.pipeline()
            
            # Always increment total visits and track unique IPs
            pipe.incr(total_visits_key)
            pipe.sadd(unique_visits_key, client_ip)
            pipe.expire(total_visits_key, timedelta(days=self.expiry_days))
            pipe.expire(unique_visits_key, timedelta(days=self.expiry_days))
            
            # Only process user tracking if token is provided
            if token:
                try:
                    user_info = await get_current_user(token)
                    user_id = user_info["user_id"]
                    pipe.sadd(user_visits_key, user_id)
                    pipe.expire(user_visits_key, timedelta(days=self.expiry_days))
                except:
                    logger.debug("Invalid token provided, skipping user tracking")
            # Store visit details in Redis
            pipe.hmset(visitor_detail_key, visit_details)
            pipe.expire(visitor_detail_key, timedelta(days=self.expiry_days))
                    
            pipe.execute()
            return True
        except RedisError as e:
            logger.error(f"Redis error tracking visit for product {product_id}: {e}")
            return False
    def get_top_visited_products(self, limit: int = 10) -> List[dict]:
        """Get the top visited products based on total visits and unique visitors"""
        try:
            result = []
            # Scan for all product visit keys
            for key in self.redis.scan_iter(match="product:*:total_visits"):
                # Handle both string and bytes key types
                key_str = key if isinstance(key, str) else key.decode()
                product_id = int(key_str.split(':')[1])
                
                # Get total visits
                total_visits = int(self.redis.get(key) or 0)
                
                # Get unique visits
                unique_visits_key = f"product:{product_id}:unique_visits"
                unique_visits = self.redis.scard(unique_visits_key) or 0
                
                # Get user visits
                user_visits_key = f"product:{product_id}:user_visits"
                user_visits = self.redis.scard(user_visits_key) or 0
                
                result.append({
                    "product_id": product_id, 
                    "total_visits": total_visits,
                    "unique_visits": unique_visits,
                    "user_visits": user_visits
                })
            
            # Sort by total visits in descending order and limit results
            return sorted(result, key=lambda x: x["total_visits"], reverse=True)[:limit]
        except RedisError as e:
            logger.error(f"Redis error getting top visited products: {e}")
            return []
    def get_visit_metrics(self, product_id: int) -> Optional[VisitMetrics]:
        """Get current visit metrics for a product"""
        total_visits_key, unique_visits_key, visitor_detail_key = self._get_keys(product_id)
        user_visits_key = f"product:{product_id}:user_visits"
        
        try:
            # Use pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Queue up all the Redis commands
            pipe.get(total_visits_key)
            pipe.scard(unique_visits_key)
            pipe.scard(user_visits_key)
            
            # Execute pipeline and get results
            total_visits, unique_visits, user_visits = pipe.execute()
            
            # Convert total_visits to int, defaulting to 0 if None
            total_visits = int(total_visits or 0)
            
            if total_visits == 0 and unique_visits == 0:
                return None
                
            return VisitMetrics(
                total_visits=total_visits,
                unique_visits=unique_visits,
                user_visits=user_visits
            )
        except RedisError as e:
            logger.error(f"Redis error getting metrics for product {product_id}: {e}")
            return None
    def get_all_product_metrics(self):
        """Get metrics for all products that have visit data"""
        metrics = {}
        try:
            # Use scan_iter instead of keys for better performance with large datasets
            for key in self.redis.scan_iter(match="product:*:*"):
                # Handle both string and bytes key types
                key_str = key.decode() if isinstance(key, bytes) else key
                try:
                    product_id = int(key_str.split(':')[1])
                except (IndexError, ValueError):
                    continue  # Skip invalid keys
                    
                total_key, unique_key, _ = self._get_keys(product_id)
                user_visits_key = f"product:{product_id}:user_visits"
                
                # Use pipeline for atomic operations
                pipe = self.redis.pipeline()
                pipe.get(total_key)
                pipe.scard(unique_key)
                pipe.scard(user_visits_key)
                
                try:
                    # Execute pipeline and get results
                    total_visits, unique_visits, user_visits = pipe.execute()
                    
                    # Convert total_visits to int, defaulting to 0 if None
                    total_visits = int(total_visits or 0)
                    
                    # Only include products that have actual visits
                    if total_visits > 0 or unique_visits > 0 or user_visits > 0:
                        metrics[product_id] = {
                            'total_visits': total_visits,
                            'unique_visits': unique_visits,
                            'user_visits': user_visits
                        }
                except Exception as e:
                    logger.error(f"Error processing metrics for product {product_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
        return metrics

    async def clear_visit_data(self, product_id: int = None) -> bool:
        """
        Clear visit data from Redis for a specific product or all products.
        
        Args:
            product_id (int, optional): Specific product ID to clear. If None, clears all products.
            
        Returns:
            bool: True if clearing was successful, False otherwise
        """
        try:
            if product_id:
                # Clear specific product data
                total_visits_key, unique_visits_key, _ = self._get_keys(product_id)
                user_visits_key = f"product:{product_id}:user_visits"
                
                # Get all visitor detail keys for this product
                visitor_keys = list(self.redis.scan_iter(
                    match=f"product:{product_id}:visitor:*"
                ))
                
                # Combine all keys to delete
                keys_to_delete = [
                    total_visits_key, 
                    unique_visits_key, 
                    user_visits_key,
                    *visitor_keys
                ]
            else:
                # Clear all product data including visitor details
                keys_to_delete = list(self.redis.scan_iter(match="product:*"))
            
            if keys_to_delete:
                # Delete in batches to avoid memory issues
                batch_size = 1000
                for i in range(0, len(keys_to_delete), batch_size):
                    batch = keys_to_delete[i:i + batch_size]
                    self.redis.delete(*batch)
                    
            return True
            
        except RedisError as e:
            logger.error(f"Redis error clearing visit data: {e}")
            return False




def get_visit_tracker(redis: Redis = Depends(get_redis_client)):
    return VisitTracker(redis)