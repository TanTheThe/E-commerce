from typing import Optional, List, Dict, Any
from sqlalchemy import ColumnElement
from src.database.models import Categories, Cart, Cart_Item
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_, update, delete
from sqlalchemy.orm import noload
from datetime import datetime
from src.errors.categories import CategoriesException
from uuid import UUID

from src.schemas.cart import CartItemCreateModel


class CartRepository:
    async def create_cart(self, user_id: str, session: AsyncSession):
        user_uuid = UUID(user_id)
        new_cart = Cart(
            user_id=user_uuid,
            created_at=datetime.now(),
        )

        session.add(new_cart)
        await session.flush()
        return new_cart

    async def create_cart_item(self, cart_item: CartItemCreateModel, session: AsyncSession):
        cart_item_dict = cart_item.model_dump()

        new_cart = Cart_Item(
            **cart_item_dict,
            created_at=datetime.now()
        )
        session.add(new_cart)
        await session.flush()
        return new_cart


    async def get_cart(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, joins: list = None):
        statement = select(Cart).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.one_or_none()

    async def get_cart_item(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, joins: list = None):
        statement = select(Cart_Item).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.one_or_none()

    async def get_all_cart_item(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, joins: list = None):
        statement = select(Cart_Item).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.all()

    async def get_cart_with_paginated_items(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession,
                                            joins: list = None, skip: int = 0, limit: int = 10):
        count_stmt = select(func.count(Cart_Item.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total_count = total_result.one()

        statement = select(Cart_Item).options(
            *joins if joins else []
        ).order_by(Cart_Item.product_id, Cart_Item.created_at.desc()).where(*conditions).offset(skip).limit(limit)

        result = await session.exec(statement)
        cart_items = result.all()
        return cart_items, total_count

    async def update_cart(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any],
                                        session: AsyncSession):
        stmt = (
            update(Cart)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)

    async def update_cart_item(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any],
                                        session: AsyncSession):
        stmt = (
            update(Cart_Item)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)

    async def hard_delete_cart_item(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        stmt = delete(Cart_Item).where(condition)
        result = await session.exec(stmt)
        return result.rowcount