from datetime import datetime
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Setup2FAAttempt
from src.cache.cache_service import CacheService
import logging

from src.errors.authentication import AuthException

logger = logging.getLogger(__name__)

cache_service = CacheService()

MAX_SETUP_ATTEMPTS = 3          # Max 3 lần setup trong window
SETUP_WINDOW_MINUTES = 15       # 15 phút
SETUP_WINDOW_SECONDS = SETUP_WINDOW_MINUTES * 60

class Setup2FASecurityService:
    async def check_rate_limit_setup_2fa(self, user_id: str, session: AsyncSession):
        try:
            rate_key = f"auth:2fa_setup:{user_id}"
            
            attempts = await cache_service.get(rate_key, default=0)
            
            if isinstance(attempts, str):
                attempts = int(attempts)
                
            if attempts >= MAX_SETUP_ATTEMPTS:
                ttl = await cache_service.ttl(rate_key)
                remaining_minutes = max(1, int(ttl / 60))
                
                logger.warning(
                    f"2FA setup rate limit exceeded for user: {user_id}, "
                    f"attempts: {attempts}"
                )
                AuthException.too_many_2fa_setup(remaining_minutes)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking setup 2FA rate limit: {str(e)}")


    async def log_setup_2fa_attempt(self, user_id: str, session: AsyncSession):
        try:
            rate_key = f"auth:2fa_setup:{user_id}"
            attempts = await cache_service.increment(rate_key)
            
            if attempts == 1:
                await cache_service.expire(rate_key, SETUP_WINDOW_SECONDS)
                
            try:
                setup_attempt = Setup2FAAttempt(
                    user_id=user_id,
                    attempted_at=datetime.now()
                )
                session.add(setup_attempt)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to log 2FA setup attempt to DB: {str(e)}")

        except Exception as e:
            logger.error(f"Error logging 2FA setup attempt: {str(e)}")
            
    
    async def reset_setup_attempts(self, user_id: str) -> bool:
        try:
            rate_key = f"auth:2fa_setup:{user_id}"
            await cache_service.delete(rate_key)
            logger.info(f"2FA setup attempts reset for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset 2FA setup attempts: {str(e)}")
            return False
    
