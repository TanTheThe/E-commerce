from typing import Optional, Dict, Any

from sqlalchemy import ColumnElement, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import PaymentRefund

class PaymentRefundRepository:
    async def create_refund(self, refund_dict: dict, session: AsyncSession):
        refund = PaymentRefund(**refund_dict)
        session.add(refund)

        return refund

    async def get_payment_refund(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None,
                                 for_update: Optional[bool] = False):
        statement = select(PaymentRefund).where(conditions).options(*joins if joins else [])
        if for_update:
            statement = statement.with_for_update()

        result = await session.exec(statement)

        return result.first()

    async def update_payment_refund(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(PaymentRefund)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)