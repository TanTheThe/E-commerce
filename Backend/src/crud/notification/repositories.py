from typing import Optional, List, Dict, Any
from sqlalchemy import ColumnElement, update
from sqlalchemy.orm import noload, load_only

from src.database.models import Color, Notification
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, desc, or_
from datetime import datetime
from src.errors.color import ColorException


class NotificationRepository:
    async def create_notification(self, notification_dict, session: AsyncSession):
        new_notification = Notification(
            **notification_dict,
            created_at=datetime.now()
        )
        session.add(new_notification)
        return new_notification


    async def get_all_notifications(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession,
                                   joins: list = None, skip: int = 0, limit: int = 30):
        count_stmt = select(func.count(Notification.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Notification).options(
            *joins if joins else []
        ).where(*conditions).offset(skip).limit(limit).order_by(desc(Notification.created_at))

        result = await session.exec(statement)
        notifications = result.all()

        return notifications, total


    async def get_notification(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, joins: list = None):
        statement = select(Notification).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.one_or_none()


    async def get_notifications_by_ids(self, session: AsyncSession, notification_ids: List[str], user_id: Optional[str] = None):
        conditions = [Notification.id.in_(notification_ids)]

        if user_id:
            conditions.append(
                or_(
                    Notification.recipient_type == "admin",
                    and_(
                        Notification.recipient_type == "customer",
                        Notification.recipient_id == user_id
                    )
                )
            )

        statement = select(Notification).where(*conditions)
        result = await session.exec(statement)
        return result.all()


    async def update_notification(self, condition: List[Optional[ColumnElement[bool]]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Notification)
            .where(*condition)
            .values(**values)
        )
        result = await session.exec(stmt)
        await session.commit()

        return result.rowcount
