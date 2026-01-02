import logging
from src.cache.cache_keys import CacheKeys
from src.cache.cache_service import CacheService
from src.errors.authentication import AuthException

logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
LOCKOUT_DURATION_SECONDS = LOCKOUT_DURATION_MINUTES * 60

cache_keys = CacheKeys()
cache_service = CacheService()

class AccountLockoutService:
    
    #============================ CHECK ACCOUNT LOCKOUT =====================================
    async def check_account_lockout(self, email: str):
        lock_key = self.get_account_lock_key(email)
        failed_key = self.get_failed_attempts_key(email)
        
        is_locked = await cache_service.exists(lock_key)
        
        if is_locked:
            ttl = await cache_service.ttl(lock_key)
            remaining_minutes = max(1, int(ttl / 60))
            
            logger.warning(f"Account locked: {email}, remaining: {remaining_minutes} minutes")
            AuthException.time_lock_remaining(remaining_minutes)
            
        failed_count = await cache_service.get(failed_key, default=0)
        
        if isinstance(failed_count, str):
            failed_count = int(failed_count)
        
        if failed_count >= MAX_FAILED_ATTEMPTS:
            await self.lock_account(email)
            logger.warning(f"Account locked due to {failed_count} failed attempts: {email}")
            AuthException.time_lock_remaining(LOCKOUT_DURATION_MINUTES)
    
    # ================================== INCREMENT FAILED ATTEMPTS ===================================
    async def increment_failed_attempts(self, email: str) -> int:
        failed_key = self.get_failed_attempts_key(email)
        failed_count = await cache_service.increment(failed_key)

        if failed_count == 1:
            await cache_service.expire(failed_key, LOCKOUT_DURATION_SECONDS)
        
        logger.warning(f"Failed login attempt {failed_count}/{MAX_FAILED_ATTEMPTS}: {email}")
        
        if failed_count >= MAX_FAILED_ATTEMPTS:
            await self.lock_account(email)
            logger.warning(f"Account auto-locked: {email}")
        
        return failed_count
    
    
    # ================================== CLEAR FAILED ATTEMPTS ===================================
    async def clear_failed_attempts(self, email: str):
        failed_key = self.get_failed_attempts_key(email)
        lock_key = self.get_account_lock_key(email)
        
        await cache_service.delete(failed_key)
        await cache_service.delete(lock_key)
        
        logger.info(f"Cleared failed attempts for: {email}")
        
    
    # ================================== UNLOCK ACCOUNT =====================================
    async def unlock_account(self, email: str) -> bool:
        try:
            failed_key = self.get_failed_attempts_key(email)
            lock_key = self.get_account_lock_key(email)
            
            await cache_service.delete(failed_key)
            await cache_service.delete(lock_key)
            
            logger.info(f"Account manually unlocked: {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to unlock account: {str(e)}")
            return False
        
       
    #  ================================== GET LOCKOUT INFO =====================================
    async def get_lockout_info(self, email: str):
        try:
            failed_key = self.get_failed_attempts_key(email)
            lock_key = self.get_account_lock_key(email)
            
            failed_count = await cache_service.get(failed_key, default=0)
            is_locked = await cache_service.exists(lock_key)
            
            if isinstance(failed_count, str):
                failed_count = int(failed_count)
            
            remaining_ttl = 0
            if is_locked:
                remaining_ttl = await cache_service.ttl(lock_key)
            
            return {
                "email": email,
                "failed_attempts": failed_count,
                "max_attempts": MAX_FAILED_ATTEMPTS,
                "is_locked": is_locked,
                "remaining_lockout_seconds": remaining_ttl,
                "remaining_lockout_minutes": max(0, int(remaining_ttl / 60))
            }
        except Exception as e:
            logger.error(f"Failed to get lockout info: {str(e)}")
            return {"email": email, "error": str(e)}
    
    
    
    
    async def lock_account(self, email: str):
        lock_key = self.get_account_lock_key(email)
        await cache_service.set(
            lock_key,
            "locked",
            ttl=LOCKOUT_DURATION_SECONDS
        )
    
    @staticmethod
    def get_account_lock_key(email: str):
        return f"auth:account_locked:{email}"
    
    @staticmethod
    def get_failed_attempts_key(email: str):
        return f"auth:failed_attempts:{email}"