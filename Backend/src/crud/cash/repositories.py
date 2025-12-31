import uuid
from typing import Optional, List, Any, Tuple

from sqlalchemy import ColumnElement, func
from sqlmodel import select, and_

from src.database.models import CashTransaction
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime


class CashRepository:
    async def create_cash_transaction(self, transaction_data: dict, session: AsyncSession):
        new_transaction = CashTransaction(
            id=uuid.uuid4(),
            transaction_code=transaction_data['transaction_code'],
            transaction_type=transaction_data['transaction_type'],
            category=transaction_data['category'],
            amount=transaction_data['amount'],
            transaction_date=transaction_data.get('transaction_date', datetime.now()),
            reference_type=transaction_data.get('reference_type'),
            reference_id=transaction_data.get('reference_id'),
            reference_name=transaction_data.get('reference_name'),
            payment_method=transaction_data['payment_method'],
            notes=transaction_data.get('notes'),
            performed_by=transaction_data.get('performed_by'),
            created_at=datetime.now()
        )

        session.add(new_transaction)
        await session.flush()
        return new_transaction

    async def get_all_cash_transaction(self, session: AsyncSession,
                                       select_columns: Optional[List[Any]] = None,
                                       joins: Optional[List[Tuple[Any, dict]]] = None,
                                       where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                       group_by_columns: Optional[List[Any]] = None,
                                       having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                       order_by: Optional[Any] = None,
                                       skip: int = 0, limit: int = 10,
                                       options: Optional[list] = None):
        if select_columns is None:
            query = select(CashTransaction)
        else:
            query = select(*select_columns).select_from(CashTransaction)

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
        cashs = result.all()

        return cashs, total

    async def get_cash_transaction(self, session: AsyncSession,
                                   select_columns: Optional[List[Any]] = None,
                                   joins: Optional[List[Tuple[Any, dict]]] = None,
                                   where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                   group_by_columns: Optional[List[Any]] = None,
                                   having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                   order_by: Optional[Any] = None,
                                   options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(CashTransaction)
        else:
            query = select(*select_columns).select_from(CashTransaction)

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

        cash = result.one_or_none()

        return cash

