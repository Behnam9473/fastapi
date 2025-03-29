"""
Configuration Module

This module manages the application configuration using Pydantic's BaseSettings.
It provides a centralized location for all configuration variables and environment settings.
"""
import time
import redis
from redis.exceptions import ConnectionError
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Base
    PROJECT_NAME: str = "ZOHOOR - AR"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    # REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", None)
    REDIS_RETRY_ATTEMPTS: int = int(os.getenv("REDIS_RETRY_ATTEMPTS", 2))
    REDIS_RETRY_DELAY: int = int(os.getenv("REDIS_RETRY_DELAY", 1))

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    
    # Static files
    MEDIA_ROOT: Path = Path("media")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Creates and returns a cached instance of the Settings class."""
    return Settings()

# Move the Redis connection attempt to a separate function
def initialize_redis():
    try:
        settings = get_settings()
        redis_client = RedisSingleton.get_instance(settings)
        return redis_client
    except ConnectionError:
        logger.error("Could not establish Redis connection")
        return None

# Remove the automatic Redis connection attempt
settings = get_settings()


class RedisSingleton:
    """Singleton class to manage a Redis client instance."""

    # Class variable to store the single Redis client instance
    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_instance(cls, settings: Settings) -> redis.Redis:
        """
        Retrieve the Redis client instance. If it does not exist, initialize it.

        Args:
            settings (Settings): The application settings with Redis configurations.

        Returns:
            redis.Redis: The initialized Redis client instance.
        """
        # Check if the instance already exists
        if cls._instance is None:
            # If not, initialize it using the private method
            cls._instance = cls._initialize_redis(settings)
        return cls._instance

    @classmethod
    def _initialize_redis(cls, settings: Settings) -> redis.Redis:
        """
        Initialize the Redis client with retry logic.

        Args:
            settings (Settings): The application settings with Redis configurations.

        Returns:
            redis.Redis: The Redis client instance after successful connection.

        Raises:
            ConnectionError: If the client fails to connect after all retry attempts.
        """
        # Retry logic for connecting to Redis
        for attempt in range(settings.REDIS_RETRY_ATTEMPTS):
            try:
                # Create a Redis client using settings
                client = redis.Redis(
                    host=settings.REDIS_HOST,     # Redis server hostname
                    port=settings.REDIS_PORT,     # Redis server port
                    db=settings.REDIS_DB,         # Redis database index
                    # password=settings.REDIS_PASSWORD,  # Uncomment if password is needed
                    decode_responses=True,        # Get responses as strings (not bytes)
                    socket_timeout=5,             # Set socket timeout in seconds
                )
                # Test the connection by pinging Redis
                client.ping()
                logger.info("Successfully connected to Redis")  # Log successful connection
                return client  # Return the connected Redis client
            except ConnectionError as e:
                # Log the failed attempt
                if attempt == settings.REDIS_RETRY_ATTEMPTS - 1:
                    logger.error(f"Failed to connect to Redis after {settings.REDIS_RETRY_ATTEMPTS} attempts")
                    raise  # Raise an error if all retry attempts fail
                logger.warning(f"Redis connection attempt {attempt + 1} failed, retrying...")
                time.sleep(settings.REDIS_RETRY_DELAY)  # Wait before the next retry
