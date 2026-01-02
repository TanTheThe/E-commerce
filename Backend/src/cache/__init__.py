import re
from src.cache.redis_manager import RedisManager
from src.cache.cache_service import CacheService
from src.cache.cache_keys import CacheKeys
from src.cache.decorators import (
    cached,
    invalidate_cache,
    cache_aside,
    rate_limit
)

redis_manager = RedisManager()
cache_service = CacheService()

__all__ = [
    "redis_manager",
    "cache_service",
    "CacheKeys",
    "cached",
    "invalidate_cache",
    "cache_aside",
    "rate_limit"
]