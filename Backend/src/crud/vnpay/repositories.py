from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement
from src.database.models import Payment
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func, update
from sqlalchemy.orm import noload
from datetime import datetime


class VNPayRepository:
    async def create_payment(self, payment_data, session: AsyncSession):
        new_payment = Payment(
            **payment_data
        )
        new_payment.created_at = datetime.now()
        session.add(new_payment)

        return new_payment


    async def get_payment(self, session: AsyncSession,
                        select_columns: Optional[List[Any]] = None,
                        joins: Optional[List[Tuple[Any, dict]]] = None,
                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                        group_by_columns: Optional[List[Any]] = None,
                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                        order_by: Optional[Any] = None,
                        options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(Payment)
        else:
            query = select(*select_columns).select_from(Payment)

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

        payment = result.one_or_none()

        return payment


    async def update_payment(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Payment)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)

    



