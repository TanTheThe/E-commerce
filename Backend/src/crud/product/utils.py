import re
from unidecode import unidecode
import asyncio
from src.cache import cache_service, CacheKeys
import logging

logger = logging.getLogger(__name__)

def generate_slug(text: str) -> str:
    text = unidecode(text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

def product_related_pattern(product_id: str = None) -> str:
    if product_id:
        return f"product:related:{product_id}:*"
    return f"product:related:*"

async def invalidate_all_product_caches():
    await asyncio.gather(
        cache_service.delete_pattern(CacheKeys.product_list_all_pattern()),
        cache_service.delete_pattern(CacheKeys.product_popular_pattern()),
        cache_service.delete_pattern(CacheKeys.product_latest_pattern()),
        cache_service.delete_pattern(CacheKeys.product_top_discount_pattern()),
        cache_service.delete_pattern(CacheKeys.product_detail_customer_pattern()),
        cache_service.delete_pattern(CacheKeys.product_related_pattern()),
        cache_service.delete_pattern(CacheKeys.product_filter_info_pattern()),
        cache_service.delete_pattern(CacheKeys.product_selectbox_pattern()),
        cache_service.delete_pattern(CacheKeys.product_variants_selectbox_pattern()),
    )
    logger.info("Invalidated all product caches")