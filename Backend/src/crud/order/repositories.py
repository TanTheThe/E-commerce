from typing import Optional, List
from sqlalchemy import ColumnElement
from sqlalchemy.orm import noload, load_only
from src.database.models import Order
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func, distinct
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
        statement = select(Order).options(
            *joins if joins else []
        ).where(conditions)

        result = await session.exec(statement)

        return result.one_or_none()


    async def get_all_order(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, order_by: list = None, skip: int = 0,
                            limit: int = 10, joins: list = None, join_user: bool = False):
        count_stmt = select(func.count(distinct(Order.id))).select_from(Order).where(*conditions)
        if join_user:
            count_stmt = count_stmt.join(Order.user)

        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Order).distinct(Order.id).options(
            noload(Order.order_detail),
            *joins if joins else []
        ).where(*conditions)

        if order_by:
            statement = statement.order_by(Order.id, *order_by)
        else:
            statement = statement.order_by(Order.id)

        statement = statement.offset(skip).limit(limit)

        result = await session.exec(statement)
        orders = result.all()

        return orders, total


    async def count_orders(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        base_condition = Order.deleted_at.is_(None)

        if conditions is not None:
            base_condition = and_(base_condition, conditions)

        statement = (
            select(Order)
            .options(
                load_only(Order.id),
                noload(Order.user),
                noload(Order.order_detail),
            )
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
