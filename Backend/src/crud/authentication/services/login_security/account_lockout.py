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
        lock_key = cache_keys.get_account_lock_key(email)
        failed_key = cache_keys.get_failed_attempts_key(email)
        
        is_locked = await cache_service.exists(lock_key)
        
        if is_locked:
            ttl = await cache_service.ttl(lock_key)
            remaining_minutes = max(1, int(ttl / 60))
            
            logger.warning(f"Tài khoản bị khóa: {email}, thời gian còn lại: {remaining_minutes} phút")
            AuthException.time_lock_remaining(remaining_minutes)
            
        failed_count = await cache_service.get(failed_key, default=0)
        
        if isinstance(failed_count, str):
            failed_count = int(failed_count)
        
        if failed_count >= MAX_FAILED_ATTEMPTS:
            await self.lock_account(email)
            logger.warning(f"Tài khoản bị khóa do đăng nhập thất bại {failed_count} lần: {email}")
            AuthException.time_lock_remaining(LOCKOUT_DURATION_MINUTES)
    
    # ================================== INCREMENT FAILED ATTEMPTS ===================================
    async def increment_failed_attempts(self, email: str) -> int:
        failed_key = cache_keys.get_failed_attempts_key(email)
        failed_count = await cache_service.increment(failed_key)

        if failed_count == 1:
            await cache_service.expire(failed_key, LOCKOUT_DURATION_SECONDS)
        
        logger.warning(f"Đăng nhập thất bại {failed_count}/{MAX_FAILED_ATTEMPTS} lần: {email}")
        
        if failed_count >= MAX_FAILED_ATTEMPTS:
            await self.lock_account(email)
            logger.warning(f"Tài khoản đã bị tự động khóa: {email}")
        
        return failed_count
    
    
    # ================================== CLEAR FAILED ATTEMPTS ===================================
    async def clear_failed_attempts(self, email: str):
        failed_key = cache_keys.get_failed_attempts_key(email)
        lock_key = cache_keys.get_account_lock_key(email)
        
        await cache_service.delete(failed_key)
        await cache_service.delete(lock_key)
        
        logger.info(f"Đã xóa số lần đăng nhập thất bại cho: {email}")
        
    
    # ================================== UNLOCK ACCOUNT =====================================
    async def unlock_account(self, email: str) -> bool:
        try:
            failed_key = cache_keys.get_failed_attempts_key(email)
            lock_key = cache_keys.get_account_lock_key(email)
            
            await cache_service.delete(failed_key)
            await cache_service.delete(lock_key)
            
            logger.info(f"Tài khoản đã được mở khóa thủ công: {email}")
            return True
        except Exception as e:
            logger.error(f"Không thể mở khóa tài khoản: {str(e)}")
            return False

    # ================================== LOCK ACCOUNT =====================================

    async def lock_account(self, email: str):
        lock_key = cache_keys.get_account_lock_key(email)
        await cache_service.set(
            lock_key,
            "locked",
            ttl=LOCKOUT_DURATION_SECONDS
        )
    
