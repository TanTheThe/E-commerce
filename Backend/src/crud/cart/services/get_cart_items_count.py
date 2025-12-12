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


class GetCartItemCountService:
    async def get_cart_items_count(self, user_id: str, session: AsyncSession):
        condition_check_user_cart = [
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None)
        ]
        cart = await cart_repository.get_cart(session=session, where_conditions=condition_check_user_cart)

        if not cart:
            CartException.cart_not_found()

        if not cart.id:
            CartException.cart_not_found()

        count = await cart_repository.get_count_cart_item(cart.id, session)

        if count < 0:
            count = 0

        return {
            "count_cart_items": count
        }