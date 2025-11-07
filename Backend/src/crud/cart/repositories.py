from typing import Optional, List, Dict, Any, Tuple
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
    
    async def get_count_cart_item(self, card_id, session: AsyncSession):
        statement = select(
            func.coalesce(func.sum(Cart_Item.quantity), 0).label("total_quantity")
        ).where(
            Cart_Item.cart_id == card_id,
            Cart_Item.deleted_at.is_(None)
        )

        result = await session.exec(statement)
        return result.one_or_none()


    async def get_all_cart_items(self, session: AsyncSession,
                                    select_columns: Optional[List[Any]] = None,
                                    joins: Optional[List[Tuple[Any, dict]]] = None,
                                    where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    group_by_columns: Optional[List[Any]] = None,
                                    having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    order_by: Optional[Any] = None,
                                    skip: int = 0, limit: int = 10,
                                    options: Optional[list] = None):

        if select_columns is None:
            query = select(Cart_Item)
        else:
            query = select(*select_columns).select_from(Cart_Item)

        if joins:
            for table, config in joins:
                if config.get('type') == 'outer':
                    query = query.outerjoin(table, config['on'])
                else:
                    query = query.join(table, config['on'])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.exec(count_query)
        total = count_result.one() or 0

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        items = result.all()

        return items, total


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