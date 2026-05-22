import logging
from src.cache import CacheService, CacheKeys
from src.errors.authentication import AuthException

logger = logging.getLogger(__name__)

cache_service = CacheService()

SIGNUP_WINDOW_MINUTES = 60          # Trong 1 giờ

MAX_VERIFICATION_ATTEMPTS = 10      # Max 10 lần click verify link
VERIFICATION_WINDOW_MINUTES = 60    # Trong 1 giờ


class VerificationSecurityService:
    async def check_verification_rate_limit(self, user_id: str):
        try:
            rate_key = CacheKeys.check_verify_rate_limit(user_id)
            
            attempts = await cache_service.get(rate_key, default=0)
            
            if isinstance(attempts, str):
                attempts = int(attempts)
            
            if attempts >= MAX_VERIFICATION_ATTEMPTS:
                ttl = await cache_service.ttl(rate_key)
                remaining_minutes = max(1, int(ttl / 60))
                
                logger.warning(
                    f"Verification rate limit exceeded for user: {user_id}"
                )
                
                AuthException.too_many_verification_attempts(remaining_minutes)
            
            new_attempts = await cache_service.increment(rate_key)
            
            if new_attempts == 1:
                await cache_service.expire(rate_key, VERIFICATION_WINDOW_MINUTES * 60)
            
        except Exception as e:
            logger.error(f"Error checking verification rate limit: {str(e)}")
            raise
    
    
    
    
    
    
    
                
                