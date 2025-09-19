from typing import Optional, List, Dict, Any
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


    async def get_all_return_orders(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession,
                                   joins: list = None, skip: int = 0, limit: int = 30):
        count_stmt = select(func.count(ReturnOrder.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(ReturnOrder).options(
            *joins if joins else []
        ).where(*conditions).offset(skip).limit(limit).order_by(desc(ReturnOrder.created_at))

        result = await session.exec(statement)
        return_orders = result.all()

        return return_orders, total


    async def get_return_order(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, joins: list = None):
        statement = select(ReturnOrder).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.one_or_none()

    async def update_return_order(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any],
                                      session: AsyncSession):
        stmt = (
            update(ReturnOrder)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)

