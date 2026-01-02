from functools import wraps
from typing import Optional, Callable, Any
import inspect
import hashlib
import json
import logging
from src.cache import cache_service
from src.cache.cache_service import CacheService

logger = logging.getLogger(__name__)

cache_service = CacheService()

def cached(key_prefix: str, ttl: Optional[int] = None, key_builder: Optional[Callable] = None):
    """
    Decorator để cache function results
    
    Args:
        key_prefix: Prefix cho cache key
        ttl: Time to live (seconds)
        key_builder: Custom function để build cache key từ args/kwargs
    
    Example:
        @cached("product:detail", ttl=3600)
        async def get_product(product_id: str):
            return await db.query(Product).filter_by(id=product_id).first()
        
        # With custom key builder
        @cached(
            "product:list",
            ttl=1800,
            key_builder=lambda category_id, page: f"{category_id}:page:{page}"
        )
        async def get_products(category_id: str, page: int = 1):
            return await db.query(Product).filter_by(category_id=category_id).all()
    """
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                key_suffix = generate_key_from_args(func, args, kwargs)
                
            cache_key = f"{key_prefix}:{key_suffix}"
            
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            logger.debug(f"Cache MISS: {cache_key}")
            
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            if result is not None:
                await cache_service.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_pattern: str):
    """
    Decorator để invalidate cache sau khi function thực thi
    Dùng cho các operations UPDATE/DELETE
    
    Args:
        key_pattern: Pattern của cache keys cần xóa (có thể dùng *)
    
    Example:
        @invalidate_cache("product:detail:*")
        async def update_product(product_id: str, data: dict):
            await db.update(Product, product_id, data)
            return {"success": True}
        
        @invalidate_cache("product:list:*")
        async def delete_product(product_id: str):
            await db.delete(Product, product_id)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            try:
                if "*" in key_pattern:
                    deleted = await cache_service.delete_pattern(key_pattern)
                    logger.info(f"Invalidated {deleted} cache keys matching: {key_pattern}")
                else:
                    await cache_service.delete(key_pattern)
                    logger.info(f"Invalidated cache key: {key_pattern}")
            except Exception as e:
                logger.error(f"Failed to invalidate cache: {e}")
            
            return result
        
        return wrapper
    return decorator


def cache_aside(key_prefix: str, ttl: Optional[int] = None, key_builder: Optional[Callable] = None, 
                invalidate_on_error: bool = False):
    """
    Cache-aside pattern với error handling
    Tự động invalidate cache nếu function raise exception
    
    Example:
        @cache_aside("order:detail", ttl=1800, invalidate_on_error=True)
        async def get_order(order_id: str):
            order = await db.get_order(order_id)
            if not order:
                raise ValueError("Order not found")
            return order
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                key_suffix = generate_key_from_args(func, args, kwargs)
            
            cache_key = f"{key_prefix}:{key_suffix}"
            
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if result is not None:
                    await cache_service.set(cache_key, result, ttl=ttl)
                
                return result
                
            except Exception as e:
                if invalidate_on_error:
                    await cache_service.delete(cache_key)
                    logger.warning(f"Invalidated cache due to error: {cache_key}")
                
                raise e
        
        return wrapper
    return decorator


def rate_limit(max_calls: int, period: int, key_builder: Optional[Callable] = None):
    """
    Decorator dùng để giới hạn số lần gọi hàm (Rate Limiting)
    
    Args:
        max_calls: Số lần gọi tối đa được phép trong một khoảng thời gian
        period: Khoảng thời gian tính bằng giây để áp dụng giới hạn
        key_builder: Hàm tùy chỉnh dùng để tạo key cho rate limit.
    
    Example:
        @rate_limit(max_calls=10, period=60)
        async def expensive_operation(user_id: str):
            # Hàm này chỉ được gọi tối đa 10 lần / 60 giây cho mỗi user
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                key = generate_key_from_args(func, args, kwargs)
            
            rate_key = f"rate_limit:{func.__name__}:{key}"
            
            from src.database.redis import check_rate_limit
            is_allowed, attempts, retry_after = await check_rate_limit(
                rate_key, max_calls, period
            )
            
            if not is_allowed:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": "Rate limit exceeded",
                        "retry_after": retry_after
                    }
                )
            
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
    
            
def generate_key_from_args(func, args, kwargs):
    """
    Generate cache key từ function arguments
    """
    sig = inspect.signature(func)
    bound_args = sig.bind_partial(*args, **kwargs)
    bound_args.apply_defaults()
    
    key_parts = []
    for param_name, param_value in bound_args.arguments.items():
        if param_name in ('self', 'cls'):
            continue
        
        if isinstance(param_value, (str, int, float, bool)):
            key_parts.append(f"{param_name}:{param_value}")
        else:
            value_hash = hash_value(param_value)
            key_parts.append(f"{param_name}:{value_hash}")
    
    return ":".join(key_parts) if key_parts else "default"


def hash_value(value: Any):
    """
    Hash một giá trị phức tạp (dict, list, object) thành string
    """
    try:
        json_str = json.dumps(value, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode()).hexdigest()[:8]
    except:
        return hashlib.md5(str(value).encode()).hexdigest()[:8]           

