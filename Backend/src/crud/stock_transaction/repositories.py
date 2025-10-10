import uuid
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from src.database.models import Warehouse, StockTransaction, Stock, Product_Variant, Product, \
    Product_Material, Product_Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, or_
from datetime import datetime


class StockTransactionRepository:
    async def create_stock_transaction(self, stock_transaction_data: dict, session: AsyncSession):
        stock_transaction = StockTransaction(
            **stock_transaction_data,
            created_at=datetime.now()
        )
        session.add(stock_transaction)

        return stock_transaction


    async def get_all_stock_transactions(self, session: AsyncSession,
                                        select_columns: Optional[List[Any]] = None,
                                        joins: Optional[List[Tuple[Any, dict]]] = None,
                                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                        group_by_columns: Optional[List[Any]] = None,
                                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                        order_by: Optional[Any] = None,
                                        skip: int = 0, limit: int = 10,
                                        options: Optional[list] = None):

        if select_columns is None:
            query = select(StockTransaction)
        else:
            query = select(*select_columns).select_from(StockTransaction)

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
        stock_transactions = result.all()

        return stock_transactions, total



