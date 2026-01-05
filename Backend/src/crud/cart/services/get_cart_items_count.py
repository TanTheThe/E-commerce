from src.crud.cart.repositories import CartRepository
from src.crud.cart.services.cart_cache import CartCacheService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Cart
from sqlmodel.ext.asyncio.session import AsyncSession

cart_repository = CartRepository()
product_variant_repository = ProductVariantRepository()
cart_cache_service = CartCacheService()


class GetCartItemCountService:
    async def get_cart_items_count(self, user_id: str, session: AsyncSession):
        cached_count = await cart_cache_service.get_cart_count_cache(user_id)
        
        if cached_count is not None:
            return {"count_cart_items": cached_count}
        
        count = await self.query_count_from_db(user_id, session)
        
        await cart_cache_service.set_cart_count_cache(user_id, count)
        
        return {"count_cart_items": count}
        
    
    async def query_count_from_db(self, user_id: str, session: AsyncSession) -> int:
        condition_check_user_cart = [
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None)
        ]
        
        cart = await cart_repository.get_cart(
            session=session, 
            where_conditions=condition_check_user_cart
        )

        if not cart or not cart.id:
            return 0

        count = await cart_repository.get_count_cart_item(cart.id, session)

        return max(0, count)