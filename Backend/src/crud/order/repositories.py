from typing import Optional
from sqlalchemy import ColumnElement
from src.database.models import Order
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func
from datetime import datetime


class OrderRepository:
    async def create_order(self, order_data, session: AsyncSession):
        if not isinstance(order_data, dict):
            order_data_dict = order_data.model_dump(exclude_none=True)
        else:
            order_data_dict = order_data

        new_order = Order(
            **order_data_dict,
            status="Pending",
            created_at=datetime.now()
        )

        session.add(new_order)
        await session.flush()

        return new_order

    async def get_order(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Order).where(conditions)
        if joins:
            statement = statement.options(*joins)

        result = await session.exec(statement)

        return result.one_or_none()

    async def get_all_order(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, skip: int = 0,
                            limit: int = 10, joins: list = None, search: str = ''):
        base_condition = Order.deleted_at.is_(None)

        if search:
            search_condition = Order.code.ilike(f"%{search}%")
            base_condition = and_(base_condition, search_condition)

        if conditions is not None:
            base_condition = and_(base_condition, conditions)

        statement = (
            select(Order)
            .where(base_condition)
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
        )

        if joins:
            statement = statement.options(*joins)

        result = await session.exec(statement)
        return result.all()

    async def count_orders(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        base_condition = Order.deleted_at.is_(None)

        if conditions is not None:
            base_condition = and_(base_condition, conditions)

        statement = (
            select(Order)
            .where(base_condition)
        )

        result = await session.exec(statement)
        return result.all()

    async def get_statistics(self, column_expr: ColumnElement, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        base_condition = Order.deleted_at.is_(None)

        if conditions is not None:
            base_condition = and_(base_condition, conditions)

        statement = select(column_expr).where(base_condition)

        result = await session.exec(statement)
        value = result.one_or_none()
        return value

    async def update_order(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()
        await session.commit()

        return data_need_update
