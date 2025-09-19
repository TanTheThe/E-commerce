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


class RemoveCartItemsService:
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

        cart_items = await cart_repository.get_all_cart_item(condition_get_all_cart_item, session,
                                                             joins_get_all_cart_item)
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
