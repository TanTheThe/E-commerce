from datetime import datetime
import logging
from src.cache import CacheService
from src.errors.authentication import AuthException

logger = logging.getLogger(__name__)

cache_service = CacheService()

MAX_SIGNUP_REQUESTS = 5             # Max 5 signups từ cùng IP
SIGNUP_WINDOW_MINUTES = 60          # Trong 1 giờ
SIGNUP_WINDOW_SECONDS = SIGNUP_WINDOW_MINUTES * 60

MAX_VERIFICATION_ATTEMPTS = 10      # Max 10 lần click verify link
VERIFICATION_WINDOW_MINUTES = 60    # Trong 1 giờ


class CreateAccountSecurityService:
    async def check_signup_rate_limit(self, ip_address: str):
        try:
            rate_key = f"auth:signup:rate:{ip_address}"
            
            attempts = await cache_service.get(rate_key, default=0)
            
            if isinstance(attempts, str):
                attempts = int(attempts)
                
            if attempts >= MAX_SIGNUP_REQUESTS:
                ttl = await cache_service.ttl(rate_key)
                remaining_minutes = max(1, int(ttl / 60))
                
                logger.warning(
                    f"Signup rate limit exceeded for IP: {ip_address}, "
                    f"attempts: {attempts}"
                )
                
                AuthException.too_many_signup_attempts(remaining_minutes)
            
            new_attempts = await cache_service.increment(rate_key)
            
            if new_attempts == 1:
                await cache_service.expire(rate_key, SIGNUP_WINDOW_SECONDS)
                
        except Exception as e:
            logger.error(f"Error checking signup rate limit: {str(e)}")
            
            
    async def check_email_signup_cooldown(self, email: str, cooldown_minutes: int = 5):
        try:
            cooldown_key = f"auth:signup:cooldown:{email}"
            
            exists = await cache_service.exists(cooldown_key)
            
            if exists:
                ttl = await cache_service.ttl(cooldown_key)
                remaining_minutes = max(1, int(ttl / 60))
                
                logger.warning(f"Email signup cooldown active: {email}")
                
                AuthException.too_many_signup_from_this_email(remaining_minutes)
            
        except Exception as e:
            logger.error(f"Failed to set email cooldown: {str(e)}")
            
    
    async def set_email_signup_cooldown(self, email: str, cooldown_minutes: int = 5):
        try:
            cooldown_key = f"auth:signup:cooldown:{email}"
            
            await cache_service.set(
                cooldown_key,
                "cooldown",
                ttl=cooldown_minutes * 60
            )
            
            logger.debug(f"Set signup cooldown for email: {email}")
            
        except Exception as e:
            logger.error(f"Failed to set email cooldown: {str(e)}")
            
            
    async def cache_verification_token(self, token: str, user_id: str, email: str, ttl: int = 86400):
        try:
            token_key = f"auth:verification:token:{token}"
            
            token_data = {
                "user_id": user_id,
                "email": email,
                "created_at": datetime.now().isoformat()
            }
            
            await cache_service.set(token_key, token_data, ttl=ttl)
            logger.debug(f"Cached verification token for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache verification token: {str(e)}")
    
    
    
    
    
    
    
                
                