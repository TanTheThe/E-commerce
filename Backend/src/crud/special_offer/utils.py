import asyncio
from typing import List

from src.cache import cache_service, CacheKeys
import logging

from src.crud.product.utils import invalidate_all_product_caches

logger = logging.getLogger(__name__)

async def invalidate_all_offer_caches():
    """Invalidate tất cả special offer caches (admin + all customers)"""
    await asyncio.gather(
        cache_service.delete_pattern(CacheKeys.special_offer_admin_list_pattern()),
        cache_service.delete_pattern(CacheKeys.special_offer_customer_list_pattern()),
    )
    logger.info("Invalidated all special offer caches")


async def invalidate_offer_and_product_caches():
    """
    Invalidate cả offer caches VÀ product caches
    Dùng khi offer được gắn/thay đổi trên products
    """
    await asyncio.gather(
        invalidate_all_offer_caches(),
        invalidate_all_product_caches(),
    )
    logger.info("Invalidated offer and product caches")


async def invalidate_customer_offer_caches(user_ids: List[str]):
    tasks = []
    for user_id in user_ids:
        tasks.append(
            cache_service.delete_pattern(
                CacheKeys.special_offer_customer_list_pattern(user_id)
            )
        )
    await asyncio.gather(*tasks)
    logger.info(f"Invalidated offer caches for {len(user_ids)} users")

