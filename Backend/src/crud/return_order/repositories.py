from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from sqlalchemy.orm import noload, load_only

from src.database.models import Color, Notification, ReturnOrder
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, desc, or_
from datetime import datetime
from src.errors.color import ColorException


class ReturnOrderRepository:
    async def create_notification(self, notification_dict, session: AsyncSession):
        new_notification = Notification(
            **notification_dict,
            created_at=datetime.now()
        )
        session.add(new_notification)
        return new_notification


    async def get_all_return_orders(self, session: AsyncSession,
                                       select_columns: Optional[List[Any]] = None,
                                       joins: Optional[List[Tuple[Any, dict]]] = None,
                                       where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                       group_by_columns: Optional[List[Any]] = None,
                                       having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                       order_by: Optional[Any] = None,
                                       skip: int = 0, limit: int = 10,
                                       options: Optional[list] = None):
        if select_columns is None:
            query = select(ReturnOrder)
        else:
            query = select(*select_columns).select_from(ReturnOrder)

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
        return_orders = result.all()

        return return_orders, total

    async def get_return_order(self, session: AsyncSession,
                               select_columns: Optional[List[Any]] = None,
                               joins: Optional[List[Tuple[Any, dict]]] = None,
                               where_conditions: Optional[List[ColumnElement[bool]]] = None,
                               group_by_columns: Optional[List[Any]] = None,
                               having_conditions: Optional[List[ColumnElement[bool]]] = None,
                               order_by: Optional[Any] = None,
                               options: Optional[List[Any]] = None,
                               for_update: Optional[bool] = False):

        if select_columns is None:
            query = select(ReturnOrder)
        else:
            query = select(*select_columns).select_from(ReturnOrder)

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

        return_order = result.one_or_none()

        return return_order


    async def update_return_order(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any],
                                      session: AsyncSession):
        stmt = (
            update(ReturnOrder)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)



