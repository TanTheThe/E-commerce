from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from sqlalchemy.dialects.postgresql import insert
from src.database.models import Notification
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func
from datetime import datetime


class NotificationRepository:
    async def create_notification(self, notification_dict, session: AsyncSession):
        new_notification = Notification(
            **notification_dict,
            created_at=datetime.now()
        )
        session.add(new_notification)
        return new_notification


    async def bulk_create_notifications(self, notifications: List, session: AsyncSession):
        stmt = insert(Notification).values(notifications)

        result = await session.execute(stmt)

        return len(notifications)


    async def get_all_notifications(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            skip: int = 0, limit: int = 10,
                            options: Optional[list] = None):
        if select_columns is None:
            query = select(Notification)
        else:
            query = select(*select_columns).select_from(Notification)

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
        notifications = result.all()

        return notifications, total

    async def get_notification(self, session: AsyncSession,
                        select_columns: Optional[List[Any]] = None,
                        joins: Optional[List[Tuple[Any, dict]]] = None,
                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                        group_by_columns: Optional[List[Any]] = None,
                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                        order_by: Optional[Any] = None,
                        options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(Notification)
        else:
            query = select(*select_columns).select_from(Notification)

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

        notification = result.one_or_none()

        return notification


    async def update_notification(self, condition: List[Optional[ColumnElement[bool]]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Notification)
            .where(*condition)
            .values(**values)
        )
        result = await session.exec(stmt)
        await session.commit()

        return result.rowcount
