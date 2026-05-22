import logging
from typing import Tuple
from fastapi import Request
from src.cache import CacheService, CacheKeys
from src.errors.authentication import AuthException

logger = logging.getLogger(__name__)

cache_service = CacheService()

MAX_REQUESTS_PER_IP_MINUTE = 15
MAX_REQUESTS_PER_IP_HOUR = 30


class RateLimiterService:
    async def check_ip_rate_limit(self, ip_address: str):
        minute_key = CacheKeys.check_ip_rate_limit_minute_key(ip_address)
        is_allowed_minute, attempts_minute, retry_after = await self.check_rate_limit_key(
            minute_key,
            max_requests=MAX_REQUESTS_PER_IP_MINUTE,
            window_seconds=60
        )
        
        if not is_allowed_minute:
            logger.warning(f"IP đã vượt quá giới hạn (phút): {ip_address}")
            AuthException.too_many_login_attempts(retry_after)
            
        hour_key = CacheKeys.check_ip_rate_limit_hour_key(ip_address)
        is_allowed_hour, attempts_hour, retry_after = await self.check_rate_limit_key(
            hour_key,
            max_requests=MAX_REQUESTS_PER_IP_HOUR,
            window_seconds=3600
        )
        
        if not is_allowed_hour:
            logger.warning(f"IP đã vượt quá giới hạn (giờ): {ip_address}")
            AuthException.too_many_login_attempts(retry_after)
            
        
    async def check_rate_limit_key(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        current = await cache_service.get(key)
        
        if current is None:
            await cache_service.set(key, 1, ttl=window_seconds)
            return True, 1, 0
        
        current = int(current)
        
        if current >= max_requests:
            ttl = await cache_service.ttl(key)
            return False, current, ttl
        
        await cache_service.increment(key)
        return True, current + 1, 0
    
    
    @staticmethod
    def get_client_ip(request: Request):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"