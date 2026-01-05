from datetime import datetime
from typing import List, Optional
from src.crud.cart.repositories import CartRepository
from src.crud.cart.services.cart_cache import CartCacheService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant, Product, Special_Offer, Cart, Cart_Item, Color
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import case, desc
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

cart_repository = CartRepository()
product_variant_repository = ProductVariantRepository()

MAX_ITEMS_PER_PAGE = 100
DEFAULT_LIMIT = 10
cart_cache_service = CartCacheService()

class GetAllCartsService:
    async def get_all_cart(self, user_id: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        if skip < 0:
            skip = 0
        if limit < 1 or limit > MAX_ITEMS_PER_PAGE:
            limit = DEFAULT_LIMIT
        
        try:   
            cached_cart = await cart_cache_service.get_cart_items_cache(user_id, skip, limit)
            
            if cached_cart is not None:
                return cached_cart.copy()
            
            cart = await self.get_user_cart(user_id, session)
            
            if not cart or not cart.id:
                return await self.get_empty_cart_response(user_id, skip, limit)
            
            cart_items, total_count = await self.get_paginated_cart_items(
                cart.id, 
                session, 
                skip, 
                limit
            )
            
            if not cart_items:
                return await self.get_empty_cart_response(user_id, skip, limit)
            
            await self.check_and_update_cart_prices(cart_items, session)
        
            cart_data = await self.format_grouped_cart_response(cart=cart,
                cart_items=cart_items,
                total_count=total_count,
                skip=skip,
                limit=limit,
                session=session
            )
            
            await cart_cache_service.warm_up_cache(user_id, cart_data, skip, limit)
            
            return cart_data
        
        except Exception as e:
            logger.error(f"Failed to get cart for user {user_id}: {str(e)}")
            raise
        
    
    async def get_user_cart(self, user_id: str, session: AsyncSession):
        condition_get_cart = [
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None)
        ]
        cart = await cart_repository.get_cart(session=session, where_conditions=condition_get_cart)
        return cart 
    
    
    async def get_paginated_cart_items(self, cart_id: str, session: AsyncSession, skip: int, limit: int):
        condition = [
            Cart_Item.cart_id == cart_id,
            Cart_Item.deleted_at.is_(None)
        ]

        joins = [
            joinedload(Cart_Item.product).options(
                joinedload(Product.special_offer).load_only(
                    Special_Offer.id,
                    Special_Offer.discount,
                    Special_Offer.type,
                    Special_Offer.name,
                    Special_Offer.used_quantity,
                    Special_Offer.total_quantity,
                    Special_Offer.start_time,
                    Special_Offer.end_time,
                    Special_Offer.deleted_at
                ),
            ).load_only(
                Product.id,
                Product.name,
                Product.status,
                Product.slug,
                Product.special_offer_id,
                Product.deleted_at
            ),
            joinedload(Cart_Item.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.id,
                    Color.name,
                    Color.code
                ),
            ).load_only(
                Product_Variant.id,
                Product_Variant.size,
                Product_Variant.color_id,
                Product_Variant.color_name,
                Product_Variant.color_code,
                Product_Variant.image,
                Product_Variant.quantity,
                Product_Variant.price,
                Product_Variant.deleted_at
            ),
        ]

        order_by = desc(Cart_Item.created_at)

        cart_items, total_count = await cart_repository.get_all_cart_items(
            session=session,
            where_conditions=condition,
            options=joins,
            skip=skip,
            limit=limit,
            order_by=order_by
        )

        return cart_items, total_count
    
    
    async def check_and_update_cart_prices(self, cart_items: List[Cart_Item], session: AsyncSession):
        items_to_update = []
        
        for cart_item in cart_items:
            if cart_item.deleted_at is not None:
                continue
                
            if not cart_item.product or not cart_item.product_variant:
                continue
                
            product = cart_item.product
            product_variant = cart_item.product_variant
            
            if product.deleted_at is not None or product.status != "active":
                continue
                
            if product_variant.deleted_at is not None:
                continue
                
            if product_variant.price is None or product_variant.price < 0:
                continue
            
            try:
                current_price = await self.calculate_current_price(product, product_variant)
            except Exception as e:
                logger.error(f"Failed to calculate price for cart item {cart_item.id}: {str(e)}")
                continue
            
            if cart_item.price != current_price:
                cart_item.price = current_price
                items_to_update.append(cart_item)
        
        if items_to_update:
            try:
                await self.bulk_update_cart_items(items_to_update, session)
            except Exception as e:
                logger.error(f"Failed to bulk update cart items: {str(e)}")


    async def calculate_current_price(self, product: Product, product_variant: Product_Variant) -> int:
        original_price = product_variant.price
        
        if original_price is None or original_price <= 0:
            return 0
        
        offer = product.special_offer
        if not self._is_offer_valid(offer):
            return original_price
        
        if not offer.discount or offer.discount <= 0:
            return original_price
        
        try:
            if offer.type == "percent":
                discount_percent = min(offer.discount, 100)
                discounted_price = original_price * (1 - discount_percent / 100)
            elif offer.type == "fixed":
                discounted_price = original_price - offer.discount
            else:
                return original_price

            discounted_price = int(round(discounted_price / 1000) * 1000)
            
            final_price = max(0, int(discounted_price))
            
            return final_price
            
        except Exception as e:
            logger.error(f"Error calculating price: {str(e)}")
            return original_price
    
    
    def _is_offer_valid(self, offer: Optional[Special_Offer]) -> bool:
        if not offer or offer.deleted_at is not None:
            return False
            
        current_time = datetime.utcnow()
        
        if offer.start_time and current_time < offer.start_time:
            return False
            
        if offer.end_time and current_time > offer.end_time:
            return False
            
        if (offer.total_quantity is not None and 
            offer.used_quantity is not None and 
            offer.used_quantity >= offer.total_quantity):
            return False
            
        return True
    
    
    def get_availability_status(self, is_available: bool, is_quantity_sufficient: bool, cart_quantity: int, max_quantity: int):
        if not is_available:
            return "out_of_stock" # Sản phẩm hết hàng hoàn toàn
        elif not is_quantity_sufficient:
            return "insufficient" # Sản phẩm có sẵn nhưng không đủ số lượng yêu cầu
        else:
            return "available"  # Sản phẩm có sẵn và đủ số lượng


    async def bulk_update_cart_items(self, cart_items: List[Cart_Item], session: AsyncSession) -> bool:
        if not cart_items:
            return False
        
        try:
            price_mapping = {item.id: item.price for item in cart_items}
            cart_item_ids = list(price_mapping.keys())

            price_case = case(
                *[(Cart_Item.id == item_id, price) for item_id, price in price_mapping.items()],
                else_=Cart_Item.price
            )

            condition = Cart_Item.id.in_(cart_item_ids)
            await cart_repository.update_cart_item(
                condition, 
                {"price": price_case, "updated_at": datetime.now()},
                session)

            await session.commit()

            return True
        
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to bulk update cart items: {str(e)}")
            raise


    async def format_grouped_cart_response(self, cart: Cart, cart_items: List[Cart_Item],
                                           total_count: int, skip: int, limit: int, session: AsyncSession):
        products_dict = {}

        for cart_item in cart_items:
            if cart_item.deleted_at is not None:
                continue

            if not cart_item.id or not cart_item.product_id or not cart_item.product_variant_id:
                continue

            if cart_item.quantity is None or cart_item.quantity <= 0:
                continue

            product = cart_item.product
            if not product or product.deleted_at is not None or product.status != "active":
                continue

            product_variant = cart_item.product_variant
            if not product_variant or product_variant.deleted_at is not None:
                continue

            product_id = str(cart_item.product_id)

            if product_id not in products_dict:
                products_dict[product_id] = {
                    "product_id": product_id,
                    "product_name": cart_item.product.name or "Unknown Product",
                    "product_slug": cart_item.product.slug or "unknown-product",
                    "variants": []
                }

            variant_info = await self.build_variant_info(cart_item, session)
            if variant_info:
                products_dict[product_id]["variants"].append(variant_info)

        products_list = list(products_dict.values())

        current_page_items_count = sum(len(product["variants"]) for product in products_list)
        current_page = skip // limit + 1 if limit > 0 else 1
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
        has_more = (skip + limit) < total_count
        
        return {
            "cart_id": str(cart.id),
            "user_id": str(cart.user_id),
            "items_count": current_page_items_count,
            "current_page": current_page,
            "per_page": limit,
            "total_pages": total_pages,
            "has_more": has_more,
            "products": products_list,
            "created_at": cart.created_at.isoformat() if cart.created_at else "",
            "total_items_in_cart": total_count,
        }


    async def get_empty_cart_response(self, user_id: str, skip: int = 0, limit: int = 10):
        current_page = skip // limit + 1 if limit > 0 else 1

        return {
            "cart_id": None,
            "user_id": user_id,
            "created_at": None,
            "total_items_in_cart": 0,
            "items_count": 0,
            "total_pages": 0,
            "has_more": False,
            "current_page": current_page,
            "per_page": limit,
            "products": []
        }


    async def build_variant_info(self, cart_item: Cart_Item, session: AsyncSession):
        if not cart_item or not cart_item.id:
            return None

        product_variant = cart_item.product_variant
        if not product_variant or product_variant.deleted_at is not None:
            return None

        if cart_item.quantity is None or cart_item.quantity <= 0:
            return None

        if cart_item.price is None or cart_item.price < 0:
            return None

        max_quantity = product_variant.quantity if (
            product_variant.quantity is not None and 
            product_variant.quantity >= 0
        ) else 0

        is_available = max_quantity > 0
        is_quantity_sufficient = cart_item.quantity <= max_quantity
        availability_status = self.get_availability_status(is_available, is_quantity_sufficient, cart_item.quantity, max_quantity)

        color_name = None
        color_code = None

        if product_variant.color_id and product_variant.color:
            color_name = product_variant.color.name
            color_code = product_variant.color.code
        else:
            color_name = product_variant.color_name
            color_code = product_variant.color_code

        return {
            "cart_item_id": str(cart_item.id),
            "product_variant_id": str(cart_item.product_variant_id),
            "size": product_variant.size if product_variant.size else None,
            "color_id": str(product_variant.color_id) if product_variant.color_id else None,
            "color_name": color_name,
            "color_code": color_code,
            "image": product_variant.image if product_variant.image else None,
            "quantity": cart_item.quantity,
            "max_quantity": max_quantity,
            "unit_price": cart_item.price,
            "selected": False,
            "is_available": is_available,
            "is_quantity_sufficient": is_quantity_sufficient,
            "availability_status": availability_status
        }
