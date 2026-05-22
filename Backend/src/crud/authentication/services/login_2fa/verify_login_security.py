import logging
from datetime import datetime
from fastapi import HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from src.cache import CacheKeys
from src.cache.cache_service import CacheService
from src.database.models import OTPVerificationAttempt
from src.errors.authentication import AuthException

logger = logging.getLogger(__name__)

cache_service = CacheService()

MAX_OTP_ATTEMPTS = 5            # Max 5 lần verify OTP
OTP_WINDOW_MINUTES = 15         # 15 phút
OTP_WINDOW_SECONDS = OTP_WINDOW_MINUTES * 60

class VerifyLoginSecurityService:
    async def check_otp_rate_limit(self, user_id: str, session: AsyncSession):
        try:
            rate_key = CacheKeys.otp_verify_attempts(user_id)
            
            attempts = await cache_service.get(rate_key, default=0)
            
            if isinstance(attempts, str):
                attempts = int(attempts)
                
            if attempts >= MAX_OTP_ATTEMPTS:
                ttl = await cache_service.ttl(rate_key)
                remaining_minutes = max(1, int(ttl / 60))
                
                logger.warning(
                    f"OTP verification rate limit exceeded for user: {user_id}, "
                    f"attempts: {attempts}"
                )
                
                AuthException.too_many_otp_verification(remaining_minutes)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking login rate limit: {str(e)}")


    async def log_otp_attempt(self, user_id: str, is_successful: bool, request: Request, session: AsyncSession):
        try:
            rate_key = CacheKeys.otp_verify_attempts(user_id)
            
            if is_successful:
                await cache_service.delete(rate_key)
                logger.info(f"OTP verification successful, cleared counter for user: {user_id}")
            else:
                attempts = await cache_service.increment(rate_key)
                
                if attempts == 1:
                    await cache_service.expire(rate_key, OTP_WINDOW_SECONDS)
                
                logger.warning(
                    f"OTP verification failed for user: {user_id}, "
                    f"attempts: {attempts}/{MAX_OTP_ATTEMPTS}"
                )
                
            try:
                ip_address = self.get_client_ip(request)
                
                otp_attempt = OTPVerificationAttempt(
                    user_id=user_id,
                    ip_address=ip_address,
                    is_successful=is_successful,
                    attempted_at=datetime.now()
                )
                session.add(otp_attempt)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to log OTP attempt to DB: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error logging OTP attempt: {str(e)}")
            
            
    async def reset_otp_attempts(self, user_id: str) -> bool:
        try:
            rate_key = CacheKeys.otp_verify_attempts(user_id)
            await cache_service.delete(rate_key)
            logger.info(f"OTP verification attempts reset for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset OTP attempts: {str(e)}")
            return False
            
            
    @staticmethod
    def get_client_ip(request: Request):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"