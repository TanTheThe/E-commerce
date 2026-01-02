from redis import asyncio as aioredis
from typing import Optional
import logging
from src.config import Settings

logger = logging.getLogger(__name__)

""" Quản lý kết nối Redis với connection pooling và lifecycle management """

class RedisManager:
    _instance: Optional['RedisManager'] = None
    _redis: Optional[aioredis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """
        Khởi tạo kết nối Redis với connection pool
        Gọi trong startup event của FastAPI
        """
        if self._redis is not None:
            logger.warning("Redis already connected")
            return

        try:
            self._redis = await aioredis.from_url(
                Settings.redis_url,
                encoding="utf-8",
                decode_responses=Settings.REDIS_DECODE_RESPONSES,
                max_connections=Settings.REDIS_MAX_CONNECTIONS,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )

            await self._redis.ping()

            logger.info(f"Redis connected successfully at {Settings.REDIS_HOST}:{Settings.REDIS_PORT}")

            info = await self._redis.info()
            logger.info(f"Redis version: {info.get('redis_version', 'unknown')}")
            logger.info(f"Redis mode: {info.get('redis_mode', 'unknown')}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise


    async def disconnect(self) -> None:
        """
        Đóng kết nối Redis
        Gọi trong shutdown event của FastAPI
        """
        if self._redis is None:
            logger.warning("Redis not connected")
            return

        try:
            await self._redis.close()
            await self._redis.connection_pool.disconnect()
            self._redis = None
            logger.info("Redis disconnected successfully")
        except Exception as e:
            logger.error(f"Error disconnecting Redis: {e}")

    @property
    def redis(self) -> aioredis.Redis:
        """
        Lấy Redis client instance
        Raise exception nếu chưa connect
        """
        if self._redis is None:
            raise RuntimeError(
                "Redis not connected. Call await redis_manager.connect() first."
            )
        return self._redis

    async def health_check(self):
        """Kiểm tra trạng thái Redis"""
        try:
            await self._redis.ping()
            info = await self._redis.info()

            return {
                "status": "healthy",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "version": info.get("redis_version", "unknown")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def clear_all(self) -> bool:
        """
        XÓA TẤT CẢ CACHE - CHỈ DÙNG CHO DEVELOPMENT/TESTING
        NGUY HIỂM - KHÔNG DÙNG TRONG PRODUCTION!
        """
        try:
            await self._redis.flushdb()
            logger.warning("All Redis cache cleared!")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    async def get_stats(self) -> dict:
        """Lấy thống kê cache"""
        try:
            info = await self._redis.info("stats")
            keyspace = await self._redis.info("keyspace")

            db_info = keyspace.get(f"db{Settings.REDIS_DB}", {})

            return {
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "total_keys": db_info.get("keys", 0),
                "expires": db_info.get("expires", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int):
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)