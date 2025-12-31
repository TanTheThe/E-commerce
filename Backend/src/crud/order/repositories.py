from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement
from sqlalchemy.orm import load_only
from src.database.models import Order, OrderStatusHistory
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func, update
from datetime import datetime
import uuid


class OrderRepository:
    async def create_order(self, order_data, session: AsyncSession):
        if not isinstance(order_data, dict):
            order_data_dict = order_data.model_dump(exclude_none=True)
        else:
            order_data_dict = order_data

        new_order = Order(
            **order_data_dict,
            created_at=datetime.now()
        )

        session.add(new_order)
        await session.flush()

        return new_order


    async def create_order_status_history(self, order_data, session: AsyncSession):
        if not isinstance(order_data, dict):
            order_data_dict = order_data.model_dump(exclude_none=True)
        else:
            order_data_dict = order_data

        new_order_history = OrderStatusHistory(
            **order_data_dict,
        )

        session.add(new_order_history)
        await session.flush()

        return new_order_history


    async def get_all_order(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            skip: int = 0, limit: int = 10,
                            options: Optional[list] = None):
        if select_columns is None:
            query = select(Order)
        else:
            query = select(*select_columns).select_from(Order)

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
        orders = result.all()

        return orders, total

    async def get_order(self, session: AsyncSession,
                        select_columns: Optional[List[Any]] = None,
                        joins: Optional[List[Tuple[Any, dict]]] = None,
                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                        group_by_columns: Optional[List[Any]] = None,
                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                        order_by: Optional[Any] = None,
                        options: Optional[List[Any]] = None,
                        for_update: Optional[bool] = False):

        if select_columns is None:
            query = select(Order)
        else:
            query = select(*select_columns).select_from(Order)

        if joins:
            for table, config in joins:
                if config.get("type") == "outer":
                    query = query.outerjoin(table, config["on"])
                else:
                    query = query.join(table, config["on"])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        if for_update:
            query = query.with_for_update()

        result = await session.exec(query)

        order = result.one_or_none()

        return order


    async def count_orders(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        base_condition = Order.deleted_at.is_(None)

        if conditions is not None:
            base_condition = and_(base_condition, conditions)

        statement = (
            select(Order)
            .options(
                load_only(Order.id),
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

    async def get_new_status_order(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(OrderStatusHistory).where(conditions).order_by(desc(OrderStatusHistory.created_at)).limit(1)

        result = await session.exec(statement)

        return result.first()

    async def update_order(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        return data_need_update

    async def update_order_some_field(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any],
                                      session: AsyncSession, get_result_back: bool = False):
        stmt = (
            update(Order)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)

    async def generate_ord_number(self, session: AsyncSession) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"ORD{today}"

        unique_suffix = uuid.uuid4().hex[:8].upper()

        return f"{prefix}{unique_suffix}"
