from datetime import datetime
from typing import List

from src.crud.cart.repositories import CartRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant, Product, Special_Offer, User, Cart, Cart_Item, Color
from src.errors.cart import CartException
from src.errors.product import ProductException
from src.schemas.cart import CartCreateModel, CartItemCreateModel, CartItemsDeleteModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, select, func, or_
from sqlalchemy.orm import selectinload, joinedload
import uuid
import time

cart_repository = CartRepository()
product_variant_repository = ProductVariantRepository()

class CartService:
    async def create_cart_service(self, user_id: str, cart_data: CartCreateModel, session: AsyncSession):
        condition_variant = and_(Product_Variant.id == cart_data.product_variant_id)
        joins_variant = [
            selectinload(Product_Variant.product).options(
                selectinload(Product.special_offer)
            ).load_only(
                Product.id,
                Product.name,
                Product.images,
                Product.special_offer_id
            ),
        ]
        product_variant = await product_variant_repository.get_product_variant(condition_variant, session, joins_variant)

        if not product_variant:
            ProductException.not_found_variant()

        condition_user_id = [Cart.user_id == user_id, Cart.deleted_at.is_(None)]
        joins_user_id = [
            selectinload(Cart.items).options(
                selectinload(Cart_Item.product),
                selectinload(Cart_Item.product_variant),
            ),
        ]
        cart = await cart_repository.get_cart(condition_user_id, session, joins_user_id)

        if not cart:
            cart = await cart_repository.create_cart(user_id, session)

        original_price = product_variant.price
        special_offer = product_variant.product.special_offer
        discounted_price = await self.calculate_discounted_price(original_price, special_offer, session)

        condition_check_variant_cart = [Cart_Item.product_variant_id == cart_data.product_variant_id,
                                        Cart_Item.cart_id == cart.id, Cart_Item.deleted_at.is_(None)]

        existing_cart_item = await cart_repository.get_cart_item(condition_check_variant_cart, session)

        if existing_cart_item:
            new_quantity = existing_cart_item.quantity + cart_data.quantity
            if new_quantity > product_variant.quantity:
                ProductException.not_enough_variant()

            condition_update_cart_item = and_(Cart_Item.id == existing_cart_item.id)
            await cart_repository.update_cart_item(condition_update_cart_item,
                                                   {"quantity": new_quantity, "price": discounted_price, "updated_at": datetime.now()},
                                                   session)
        else:
            if cart_data.quantity > product_variant.quantity:
                ProductException.not_enough_variant()

            cart_item_create = CartItemCreateModel(
                cart_id=cart.id,
                product_id=product_variant.product.id,
                product_variant_id=product_variant.id,
                quantity=cart_data.quantity,
                price=discounted_price
            )

            cart_item = await cart_repository.create_cart_item(cart_item_create, session)

        await session.commit()

        condition_cart_response = [Cart.id == cart.id, Cart.deleted_at.is_(None)]
        joins_cart_response = [
            selectinload(Cart.user),
            selectinload(Cart.items).options(
                selectinload(Cart_Item.product),
                selectinload(Cart_Item.product_variant),
            )
        ]
        final_cart = await cart_repository.get_cart(condition_cart_response, session, joins_cart_response)
        return await self.format_cart_response(final_cart, session)


    async def calculate_discounted_price(self, original_price, special_offer: Special_Offer, session: AsyncSession):
        if not special_offer:
            return original_price

        now = datetime.now()
        if special_offer.start_time > now or special_offer.end_time < now:
            return original_price

        if special_offer.used_quantity >= special_offer.total_quantity:
            return original_price

        discount_amount = (original_price * special_offer.discount) / 100
        final_price = original_price - discount_amount
        final_price = int(round(final_price / 1000) * 1000)

        return int(final_price)


    async def format_cart_response(self, cart: Cart, session: AsyncSession):
        items = []
        for cart_item in cart.items:
            if cart_item.deleted_at is None:
                items.append({
                    "item_id": str(cart_item.id),
                    "product_id": str(cart_item.product_id),
                    "product_name": cart_item.product.name if cart_item.product else None,
                    "product_variant_id": str(cart_item.product_variant_id),
                    "size": cart_item.product_variant.size if cart_item.product_variant else None,
                    "color_id": str(cart_item.product_variant.color_id) if cart_item.product_variant else None,
                    "color_name": cart_item.product_variant.color_name if cart_item.product_variant else None,
                    "color_code": cart_item.product_variant.color_code if cart_item.product_variant else None,
                    "sku": cart_item.product_variant.sku if cart_item.product_variant else None,
                    "image": cart_item.product_variant.image if cart_item.product_variant else None,
                    "quantity": cart_item.quantity,
                    "unit_price": cart_item.price,
                    "total_item_price": cart_item.price * cart_item.quantity,
                })

        return {
            "cart_id": str(cart.id),
            "user_id": str(cart.user_id),
            "created_at": cart.created_at.isoformat(),
            "items_count": len(items),
            "items": items
        }

    async def get_all_cart_service(self, user_id: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        condition_get_cart = [
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None)
        ]
        cart = await cart_repository.get_cart(condition_get_cart, session)
        total_count = 0

        if cart:
            condition = [Cart_Item.cart_id == cart.id, Cart_Item.deleted_at.is_(None)]
            joins = [
                joinedload(Cart_Item.product).options(
                    joinedload(Product.special_offer),
                ),
                joinedload(Cart_Item.product_variant).options(
                    joinedload(Product_Variant.color),
                ),
            ]
            cart.items, total_count = await cart_repository.get_cart_with_paginated_items(condition, session, joins, skip, limit)
        else:
            return await self.get_empty_cart_response(user_id, session, skip, limit)

        return await self.format_grouped_cart_response(cart, session)


    async def format_grouped_cart_response(self, cart: Cart, session: AsyncSession):
        products_dict = {}

        for cart_item in cart.items:
            if cart_item.deleted_at is None:
                product_id = str(cart_item.product_id)

                if product_id not in products_dict:
                    product = cart_item.product
                    products_dict[product_id] = {
                        "product_id": product_id,
                        "product_name": product.name if product else "Unknown Product",
                        "variants": []
                    }

                variant_info = await self.build_variant_info(cart_item, session)
                products_dict[product_id]["variants"].append(variant_info)

        products_list = list(products_dict.values())
        current_page_items_count = sum(len(product["variants"]) for product in products_list)

        return {
            "cart_id": str(cart.id),
            "user_id": str(cart.user_id),
            "items_count": current_page_items_count,
            "products": products_list,
            "created_at": cart.created_at.isoformat(),
        }

    async def get_empty_cart_response(self, user_id: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        return {
            "cart_id": None,
            "user_id": user_id,
            "total_items_in_cart": 0,
            "items_count": 0,
            "total_items": 0,
            "has_more": False,
            "current_page": skip // limit + 1 if limit > 0 else 1,
            "per_page": limit,
            "products": []
        }

    async def build_variant_info(self, cart_item: Cart_Item, session: AsyncSession):
        return {
            "cart_item_id": str(cart_item.id),
            "product_variant_id": str(cart_item.product_variant_id),
            "size": cart_item.product_variant.size if cart_item.product_variant else None,
            "color_id": str(cart_item.product_variant.color_id) if cart_item.product_variant else None,
            "color_name": cart_item.product_variant.color.name if cart_item.product_variant
                                                                  and cart_item.product_variant.color_id else cart_item.product_variant.color_name,
            "color_code": cart_item.product_variant.color.code if cart_item.product_variant
                                                                  and cart_item.product_variant.color_id else cart_item.product_variant.color_code,
            "image": cart_item.product_variant.image if cart_item.product_variant else None,
            "quantity": cart_item.quantity,
            "max_quantity": cart_item.product_variant.quantity if cart_item.product_variant else 0,
            "unit_price": cart_item.price,
            "selected": False
        }
    
    async def get_cart_items_count_service(self, user_id: str, session: AsyncSession):
        condition_check_user_cart = [Cart.user_id == user_id, Cart.deleted_at.is_(None)]
        cart = await cart_repository.get_cart(condition_check_user_cart, session)

        if not cart:
            CartException.cart_not_found()

        count = await cart_repository.get_count_cart_item(cart.id, session)

        return {
            "count_cart_items": count
        }

        


    async def remove_items_from_cart(self, user_id: str, data: CartItemsDeleteModel, session: AsyncSession):
        item_ids = data.item_ids
        item_uuids = [uuid.UUID(item_id) for item_id in item_ids]

        condition_check_user_cart = [Cart.user_id == user_id, Cart.deleted_at.is_(None)]
        cart = await cart_repository.get_cart(condition_check_user_cart, session)
        if not cart:
            CartException.cart_not_found()

        condition_get_all_cart_item = [
            Cart_Item.cart_id == cart.id,
            Cart_Item.id.in_(item_ids),
            Cart_Item.deleted_at.is_(None)
        ]

        joins_get_all_cart_item = [
            joinedload(Cart_Item.product),
            joinedload(Cart_Item.product_variant),
        ]

        cart_items = await cart_repository.get_all_cart_item(condition_get_all_cart_item, session, joins_get_all_cart_item)
        if not cart_items:
            CartException.cart_items_not_found()

        valid_item_ids = [item.id for item in cart_items]
        invalid_count = len(item_uuids) - len(valid_item_ids)

        condition_delete = and_(Cart_Item.id.in_(valid_item_ids))
        deleted_count = await cart_repository.hard_delete_cart_item(condition_delete, session)

        await session.commit()

        return {
            "deleted_items_count": deleted_count,
            "invalid_items_count": invalid_count
        }











