from config import RedisSingleton, get_settings

def get_redis_client():
    """
    Dependency to provide a Redis client instance.
    """
    settings = get_settings()
    return RedisSingleton.get_instance(settings)