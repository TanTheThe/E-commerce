from typing import Any, Optional
import json
import logging
from redis import asyncio as aioredis
from src.cache.redis_manager import RedisManager
import asyncio

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None

    @property
    def redis(self) -> aioredis.Redis:
        """Get Redis instance"""
        if self._redis is None:
            self._redis = RedisManager.redis
        return self._redis

    # ============================================== BASIC OPERATIONS =================================================

    async def get(self, key: str, default: Any = None, deserialize: bool = True) -> Any:
        """
        Lấy giá trị từ cache

        Args:
            key: Cache key
            default: Giá trị mặc định nếu không tìm thấy
            deserialize: Tự động deserialize JSON
        """
        try:
            value = await self.redis.get(key)

            if value is None:
                return default

            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value

            return value

        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return default

    async def set(self, key: str, value: Any, ttl: Optional[int] = None, serialize: bool = True) -> bool:
        """
        Lưu giá trị vào cache

        Args:
            key: Cache key
            value: Giá trị cần lưu
            ttl: Time to live (seconds)
            serialize: Tự động serialize thành JSON
        """
        try:
            if serialize and not isinstance(value, str):
                value = json.dumps(value, default=str)

            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)

            return True

        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Xóa một key"""
        try:
            deleted = await self.redis.delete(key)
            return deleted > 0
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Xóa nhiều keys theo pattern
        VD: delete_pattern("product:*")
        """
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern, count=100):
                keys.append(key)

            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Deleted {deleted} keys matching pattern '{pattern}'")
                return deleted
            return 0

        except Exception as e:
            logger.error(f"Cache delete pattern error for '{pattern}': {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Kiểm tra key có tồn tại không"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Lấy TTL của key (seconds). -1 = no expiry, -2 = not exist"""
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key '{key}': {e}")
            return -2

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time cho key"""
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error for key '{key}': {e}")
            return False

    # ============================================ ADVANCED OPERATIONS =================================================

    async def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """
        Cache-aside pattern: Lấy từ cache, nếu không có thì query và cache

        Args:
            key: Cache key
            factory_func: Function để lấy data nếu cache miss (có thể async)
            ttl: TTL cho cache
            *args, **kwargs: Arguments cho factory_func
        """
        cached = await self.get(key)
        if cached is not None:
            return cached

        try:
            if asyncio.iscoroutinefunction(factory_func):
                value = await factory_func(*args, **kwargs)
            else:
                value = factory_func(*args, **kwargs)

            if value is not None:
                await self.set(key, value, ttl=ttl)

            return value

        except Exception as e:
            logger.error(f"Cache get_or_set error for key '{key}': {e}")
            return None

    async def increment(self, key: str, amount: int = 1) -> int:
        """Tăng giá trị counter"""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            return 0

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Giảm giá trị counter"""
        try:
            return await self.redis.decrby(key, amount)
        except Exception as e:
            logger.error(f"Cache decrement error for key '{key}': {e}")
            return 0

    async def check_exists_with_ttl(self, key: str, ttl: int) -> bool:
        """
        Check if key exists, nếu không thì set với TTL
        Dùng cho idempotency check

        Returns:
            True nếu key đã tồn tại (duplicate), False nếu chưa (first time)
        """
        try:
            result = await self.redis.set(key, "1", nx=True, ex=ttl)
            return result is None
        except Exception as e:
            logger.error(f"Check exists error for key '{key}': {e}")
            return False

    async def acquire_lock(self, key: str, timeout: int = 10) -> bool:
        """
        Giành quyền xử lý

        Tránh deadlock, trường hợp worker chết giữa chừng
        => Lock tự động bị xóa, worker khác có thể acquire
        """
        try:
            result = await self.redis.set(key, "1", nx=True, ex=timeout)
            return result is not None
        except Exception as e:
            logger.error(f"Lock acquire error for key '{key}': {e}")
            return False

    async def release_lock(self, key: str) -> bool:
        """
        Nhả quyền xử lý

        => Xóa lock để worker khác có thể acquire
        """
        return await self.delete(key)


