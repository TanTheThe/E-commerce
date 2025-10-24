from datetime import datetime
from typing import List

from src.crud.cart.repositories import CartRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant, Product, Special_Offer, User, Cart, Cart_Item, Color
from src.errors.cart import CartException
from src.errors.product import ProductException
from src.schemas.cart import CartCreateModel, CartItemCreateModel, CartItemsDeleteModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, select, func, or_, case
from sqlalchemy.orm import selectinload, joinedload
import uuid
import time

cart_repository = CartRepository()
product_variant_repository = ProductVariantRepository()


class GetAllCartsService:
    async def get_all_cart(self, user_id: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        condition_get_cart = [
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None)
        ]

        cart = await cart_repository.get_cart(condition_get_cart, session)
        total_count = 0

        if cart:
            if not cart.id:
                return await self.get_empty_cart_response(user_id, session, skip, limit)

            condition = [
                Cart_Item.cart_id == cart.id,
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
            cart.items, total_count = await cart_repository.get_cart_with_paginated_items(
                condition, session, joins, skip, limit
            )

            await self.check_and_update_cart_prices(cart.items, session)
        else:
            return await self.get_empty_cart_response(user_id, session, skip, limit)

        return await self.format_grouped_cart_response(cart, session)
    
    async def check_and_update_cart_prices(self, cart_items: list, session: AsyncSession):
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
            
            current_price = await self.calculate_current_price(product, product_variant)
            
            if cart_item.price != current_price:
                cart_item.price = current_price
                items_to_update.append(cart_item)
        
        if items_to_update:
            await self.bulk_update_cart_items(items_to_update, session)

    async def calculate_current_price(self, product: Product, product_variant: Product_Variant) -> float:
        original_price = product_variant.price
        
        offer = product.special_offer
        valid_offer = self._is_offer_valid(offer)
        
        if not valid_offer:
            return original_price
            
        offer_type = offer.type
        offer_discount = offer.discount
        
        if offer_type and offer_discount is not None:
            if offer_type == "percent":
                raw_discounted_price = original_price * (1 - offer_discount / 100)
                discounted_price = int(round(raw_discounted_price / 1000) * 1000)
            elif offer_type == "fixed":
                raw_discounted_price = max(0, original_price - offer_discount)
                discounted_price = int(round(raw_discounted_price / 1000) * 1000)
            else:
                discounted_price = original_price
        else:
            discounted_price = original_price
            
        return max(0, discounted_price)
    
    def _is_offer_valid(self, offer) -> bool:
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
    
    def _get_availability_status(self, is_available: bool, is_quantity_sufficient: bool, cart_quantity: int, max_quantity: int) -> str:
        if not is_available:
            return "out_of_stock" # Sản phẩm hết hàng hoàn toàn
        elif not is_quantity_sufficient:
            return "insufficient" # Sản phẩm có sẵn nhưng không đủ số lượng yêu cầu
        else:
            return "available"  # Sản phẩm có sẵn và đủ số lượng

    async def bulk_update_cart_items(self, cart_items: List[Cart_Item], session: AsyncSession) -> bool:
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

    async def format_grouped_cart_response(self, cart: Cart, session: AsyncSession):
        products_dict = {}

        for cart_item in cart.items:
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
                    "product_name": product.name if product.name else "Unknown Product",
                    "product_slug": product.slug if product.slug else "unknown-product",
                    "variants": []
                }

            variant_info = await self.build_variant_info(cart_item, session)
            if variant_info:
                products_dict[product_id]["variants"].append(variant_info)

        products_list = list(products_dict.values())

        current_page_items_count = sum(len(product["variants"]) for product in products_list)

        return {
            "cart_id": str(cart.id),
            "user_id": str(cart.user_id),
            "items_count": current_page_items_count,
            "products": products_list,
            "created_at": cart.created_at.isoformat() if cart.created_at else "",
        }

    async def get_empty_cart_response(self, user_id: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        current_page = skip // limit + 1 if limit > 0 else 1

        return {
            "cart_id": None,
            "user_id": user_id,
            "total_items_in_cart": 0,
            "items_count": 0,
            "total_items": 0,
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

        max_quantity = product_variant.quantity if product_variant.quantity is not None and product_variant.quantity >= 0 else 0

        is_available = max_quantity > 0
        is_quantity_sufficient = cart_item.quantity <= max_quantity
        availability_status = self._get_availability_status(is_available, is_quantity_sufficient, cart_item.quantity, max_quantity)

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
