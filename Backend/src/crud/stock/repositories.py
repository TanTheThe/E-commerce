from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from src.database.models import Stock, Product_Variant, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, case
from datetime import datetime


class StockRepository:
    async def get_all_stocks(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None,
                             for_update: bool = False):

        if select_columns is None:
            query = select(Stock)
        else:
            query = select(*select_columns).select_from(Stock)

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

        if for_update:
            query = query.with_for_update()

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        stocks = result.all()

        return stocks, total


    async def get_stock(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            options: Optional[list] = None,
                            for_update: bool = False):

        if select_columns is None:
            query = select(Stock)
        else:
            query = select(*select_columns).select_from(Stock)

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

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        if for_update:
            query = query.with_for_update()

        result = await session.exec(query)
        stock = result.one_or_none()

        return stock


    async def create_stock(self, stock_data: dict, session: AsyncSession):
        stock = Stock(
            **stock_data,
            created_at=datetime.now()
        )
        session.add(stock)

        return stock


    async def update_stock(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Stock)
            .where(condition)
            .values(**values)
        )

        await session.exec(stmt)
