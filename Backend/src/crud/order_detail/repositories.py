from typing import Optional, List, Any, Tuple
from sqlalchemy import ColumnElement
from src.database.models import Product, Order_Detail, Order
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, func, and_
from datetime import datetime


class OrderDetailRepository:
    async def create_order_detail(self, order_detail_list, session: AsyncSession):
        new_order_details = []

        for item in order_detail_list:
            if not isinstance(item, dict):
                item_dict = item.model_dump(exclude_none=True)
            else:
                item_dict = item

            new_order_detail = Order_Detail(**item_dict)
            new_order_detail.created_at = datetime.now()
            new_order_details.append(new_order_detail)

        session.add_all(new_order_details)
        await session.flush()

    async def get_all_order_detail(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            skip: int = 0, limit: int = 10,
                            options: Optional[list] = None):
        if select_columns is None:
            query = select(Order_Detail)
        else:
            query = select(*select_columns).select_from(Order_Detail)

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
        details = result.all()

        return details, total

    async def get_order_detail(self, session: AsyncSession,
                        select_columns: Optional[List[Any]] = None,
                        joins: Optional[List[Tuple[Any, dict]]] = None,
                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                        group_by_columns: Optional[List[Any]] = None,
                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                        order_by: Optional[Any] = None,
                        options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(Order_Detail)
        else:
            query = select(*select_columns).select_from(Order_Detail)

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

        result = await session.exec(query)

        order_detail = result.one_or_none()

        return order_detail


