from src.cache.cache_service import CacheService
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


CART_ITEMS_TTL = 300  # 5 minutes - Data phức tạp, cho phép stale data ngắn
CART_COUNT_TTL = 60   # 1 minute - Cần update nhanh hơn

cache_service = CacheService()

class CartCacheService:
    async def get_cart_items_cache(self, user_id: str, skip: int, limit: int):
        try:
            cache_key = f"cart:items:user:{user_id}:page:{skip}:{limit}"
            cached_data = await cache_service.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache HIT: Cart items for user {user_id}, page {skip}/{limit}")
                return cached_data
            
            logger.info(f"Cache MISS: Cart items for user {user_id}, page {skip}/{limit}")
            return None
        
        except Exception as e:
            logger.error(f"Error getting cart items cache for user {user_id}: {e}")
            return None


    async def set_cart_items_cache(self, user_id: str, skip: int, limit: int, 
                                   cart_data: Dict[str, Any]) -> bool:
        try:
            cache_key = f"cart:items:user:{user_id}:page:{skip}:{limit}"

            success = await cache_service.set(
                cache_key, 
                cart_data, 
                ttl=CART_ITEMS_TTL
            )
            
            if success:
                logger.info(f"Cache SET: Cart items for user {user_id}, TTL={CART_ITEMS_TTL}s")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting cart items cache for user {user_id}: {e}")
            return False
        
        
    async def set_cart_count_cache(self, user_id: str, count: int) -> bool:
        try:
            cache_key = f"cart:count:user:{user_id}"
            success = await cache_service.set(
                cache_key,
                count,
                ttl=CART_COUNT_TTL
            )
            
            if success:
                logger.info(f"Cache SET: Cart count for user {user_id} = {count}, TTL={CART_COUNT_TTL}s")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting cart count cache for user {user_id}: {e}")
            return False
        
        
    async def warm_up_cache(self, user_id: str, cart_data: Dict[str, Any], 
                           skip: int, limit: int) -> bool:
        """
        Warm up cache sau khi query DB, Lưu cả items và count cùng lúc
        """
        try:
            items_cached = await self.set_cart_items_cache(user_id, skip, limit, cart_data)
            
            total_count = cart_data.get("total_items_in_cart", 0)
            count_cached = await self.set_cart_count_cache(user_id, total_count)
            
            return items_cached and count_cached
            
        except Exception as e:
            logger.error(f"Error warming up cache for user {user_id}: {e}")
            return False
        
    
    async def get_cart_count_cache(self, user_id: str) -> Optional[int]:
        try:
            cache_key = f"cart:count:user:{user_id}"
            count = await cache_service.get(cache_key)
            
            if count is not None:
                logger.info(f"Cache HIT: Cart count for user {user_id} = {count}")
                return int(count)
            
            logger.info(f"Cache MISS: Cart count for user {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting cart count cache for user {user_id}: {e}")
            return None
        
        
    async def invalidate_user_cart_cache(self, user_id: str) -> int:
        """
        Xóa TẤT CẢ cache liên quan đến cart của user
        Gọi khi: create/update/delete cart items, checkout success
        """
        try:
            pattern = f"cart:*:user:{user_id}*"
            deleted_count = await cache_service.delete_pattern(pattern)
            
            logger.info(f"Cache INVALIDATED: Deleted {deleted_count} keys for user {user_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error invalidating cart cache for user {user_id}: {e}")
            return 0
        
        
    
        
        
    