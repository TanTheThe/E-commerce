from typing import Tuple
from fastapi import Request
from src.cache import redis_manager
from src.cache.cache_keys import CacheKeys
from src.cache.redis_manager import RedisManager
from src.config import Config
from src.crud.authentication.services.token_blacklist_service import TokenBlacklistService
import logging

logger = logging.getLogger(__name__)

token_blacklist_service = TokenBlacklistService()
redis_manager = RedisManager()

async def token_in_blocklist(jti: str, request: Request) -> bool:
    """
    Kiểm tra JTI có trong blacklist không
    
    Args:
        jti: JWT Token ID
    
    Returns:
        bool: True nếu token đã bị blacklist
    """
    try:
        redis = redis_manager.redis
        key = CacheKeys.jwt_blacklist(jti)
        
        exists = await redis.exists(key)
        return exists > 0
        
    except Exception as e:
        logger.error(f"Failed to check JTI in blacklist: {e}")
        return False
    
async def check_rate_limit(key: str, max_attempts: int, window_seconds: int) -> Tuple[bool, int, int]:
    """
    Kiểm tra rate limit
    
    Args:
        key: Cache key để track (VD: rate_limit:login:192.168.1.1)
        max_attempts: Số lần tối đa cho phép
        window_seconds: Khung thời gian (seconds)
    
    Returns:
        Tuple[is_allowed, current_attempts, retry_after_seconds]
    """
    
    try:
        redis = redis_manager.redis
        
        current = await redis.get(key)
        
        if current is None:
            await redis.setex(key, window_seconds, 1)
            return True, 1, 0
        
        current = int(current)
        
        if current >= max_attempts:
            ttl = await redis.ttl(key)
            logger.warning(f"Rate limit exceeded for key: {key}")
            return False, current, ttl
        
        await redis.incr(key)
        remaining = max_attempts - current - 1
        
        return True, current + 1, 0
        
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True, 0, 0
    
async def check_login_rate_limit(identifier: str) -> Tuple[bool, int, int]:
    """
    Kiểm tra rate limit cho login
    
    Args:
        identifier: IP address hoặc username
    
    Returns:
        Tuple[is_allowed, attempts, retry_after]
    """
    key = CacheKeys.rate_limit_login(identifier)
    return await check_rate_limit(
        key,
        Config.RATE_LIMIT_LOGIN_MAX,
        Config.RATE_LIMIT_LOGIN_WINDOW
    )
    
async def check_otp_rate_limit(user_id: str) -> Tuple[bool, int, int]:
    """
    Kiểm tra rate limit cho OTP request
    
    Args:
        user_id: User ID
    
    Returns:
        Tuple[is_allowed, attempts, retry_after]
    """
    key = CacheKeys.rate_limit_otp(user_id)
    return await check_rate_limit(
        key,
        Config.RATE_LIMIT_OTP_MAX,
        Config.RATE_LIMIT_OTP_WINDOW
    )

async def reset_rate_limit(key: str) -> bool:
    """
    Reset rate limit counter (VD: sau khi login thành công)
    
    Args:
        key: Cache key
    
    Returns:
        bool: True nếu reset thành công
    """
    try:
        redis = redis_manager.redis
        deleted = await redis.delete(key)
        return deleted > 0
    except Exception as e:
        logger.error(f"Failed to reset rate limit: {e}")
        return False

