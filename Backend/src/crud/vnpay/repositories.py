from typing import Optional, List, Dict, Any
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
        await session.commit()

        return new_payment

    async def get_payment(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Payment).where(conditions).options(*joins if joins else [])
        result = await session.exec(statement)
        return result.one_or_none()

    async def update_payment(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Payment)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)



