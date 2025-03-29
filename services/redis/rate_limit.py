from redis import Redis
from fastapi import Depends, Request, HTTPException

from .redis_client import get_redis_client


class RateLimiter:
    def __init__(self, redis_client: Redis, limit: int, window: int):
        """
        Initialize the rate limiter.

        Args:
            redis_client (Redis): Redis client instance.
            limit (int): Maximum number of requests allowed in the time window.
            window (int): Time window in seconds.
        """
        self.redis_client = redis_client
        self.limit = limit
        self.window = window

    def is_allowed(self, key: str) -> bool:
        """
        Check if the request is allowed based on the rate limit.

        Args:
            key (str): Unique key for the client (e.g., IP address).

        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        current_count = self.redis_client.get(key)
        if current_count is None:
            # If the key doesn't exist, set it with an expiration time
            self.redis_client.set(key, 1, ex=self.window)
            return True
        else:
            current_count = int(current_count)
            if current_count >= self.limit:
                return False
            # Increment the request count
            self.redis_client.incr(key)
            return True


def get_rate_limiter():
    """
    Dependency to provide a RateLimiter instance.
    """
    redis_client = get_redis_client()
    # Configure rate limit: 15 requests per minute
    return RateLimiter(redis_client, limit=15, window=60)

def rate_limit(request: Request, rate_limiter: RateLimiter = Depends(get_rate_limiter)):
    """
    Dependency to enforce rate limiting.
    """
    client_ip = request.client.host  # Get the client's IP address
    rate_limit_key = f"rate_limit:{client_ip}"

    if not rate_limiter.is_allowed(rate_limit_key):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again in a minute.",
        )