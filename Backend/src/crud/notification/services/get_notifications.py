from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import func
from src.crud.notification.repositories import NotificationRepository
from src.database.models import Notification
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, select
import json
from src.schemas.notification import RecipientType
import logging

logger = logging.getLogger(__name__)

notification_repository = NotificationRepository()

class GetNotificationsService:
    def build_notification_response(self, notification: Notification) -> Dict[str, Any]:
        return {
            "id": str(notification.id),
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,

            "order_id": str(notification.order_id) if notification.order_id else None,
            "special_offer_id": str(notification.special_offer_id) if notification.special_offer_id else None,
            "return_order_id": str(notification.return_order_id) if notification.return_order_id else None,

            "sender_type": notification.sender_type,
            "sender_id": str(notification.sender_id) if notification.sender_id else None,

            "action_type": notification.action_type,
            "action_data": json.loads(notification.action_data) if notification.action_data else None,

            "is_read": notification.is_read,
            "is_processed": notification.is_processed,

            "created_at": str(notification.created_at),
            "read_at": str(notification.read_at),
            "processed_at": str(notification.processed_at),
        }

    async def get_notifications_admin(self, session: AsyncSession, unread_only: bool = False,
                                            action_required: bool = False,
                                            is_processed: Optional[bool] = None,
                                            notification_type: Optional[str] = None,
                                            sender_type: Optional[str] = None,
                                            from_date: Optional[datetime] = None,
                                            to_date: Optional[datetime] = None,
                                            sort_by: str = "created_at",
                                            sort_order: str = "desc",
                                            skip: int = 0, limit: int = 10):
        conditions = [Notification.recipient_type == RecipientType.ADMIN]

        if unread_only:
            conditions.append(Notification.is_read == False)

        if action_required:
            conditions.extend(
                [Notification.action_type.isnot(None), Notification.is_processed == False]
            )

        if is_processed is not None:
            conditions.append(Notification.is_processed == is_processed)

        if notification_type:
            conditions.append(Notification.type == notification_type)

        if sender_type:
            conditions.append(Notification.sender_type == sender_type)

        if from_date:
            conditions.append(Notification.created_at >= from_date)

        if to_date:
            to_date_end = to_date + timedelta(days=1)
            conditions.append(Notification.created_at < to_date_end)

        order_by = getattr(Notification, sort_by)
        if sort_order == "desc":
            order_by = order_by.desc()
        else:
            order_by = order_by.asc()

        notifications, total = await notification_repository.get_all_notifications(
            session=session, where_conditions=conditions, order_by=order_by, skip=skip, limit=limit
        )

        data = [self.build_notification_response(notif) for notif in notifications]

        stats = await self.get_admin_stats_quick(session, conditions)

        return {
            "data": data,
            "total": total,
            "stats": stats
        }


    async def get_admin_stats_quick(self, session: AsyncSession, base_conditions: List):
        unread_conditions = base_conditions + [Notification.is_read == False]
        unread_query = select(func.count()).select_from(Notification).where(and_(*unread_conditions))
        result_unread = await session.exec(unread_query)
        total_unread = result_unread.one() or 0

        action_conditions = base_conditions + [Notification.action_type.isnot(None), Notification.is_processed == False]
        action_query = select(func.count()).select_from(Notification).where(and_(*action_conditions))
        result_action = await session.exec(action_query)
        total_action_required = result_action.one() or 0

        unprocessed_conditions = base_conditions + [Notification.is_processed == False]
        unprocessed_query = select(func.count()).select_from(Notification).where(and_(*unprocessed_conditions))
        result_unprocessed = await session.exec(unprocessed_query)
        total_unprocessed = result_unprocessed.one() or 0

        return {
            "total_unread": total_unread,
            "total_action_required": total_action_required,
            "total_unprocessed": total_unprocessed
        }


    async def get_notifications_customer(self, session: AsyncSession, user_id: str,
                                                 unread_only: bool = False,
                                                 notification_type: Optional[str] = None,
                                                 from_date: Optional[datetime] = None,
                                                 to_date: Optional[datetime] = None,
                                                 sort_by: str = "created_at",
                                                 sort_order: str = "desc",
                                                 skip: int = 0, limit: int = 10):
        conditions = [Notification.recipient_type == RecipientType.CUSTOMER, Notification.recipient_id == user_id]

        if unread_only:
            conditions.append(Notification.is_read == False)

        if notification_type:
            conditions.append(Notification.type == notification_type)

        if from_date:
            conditions.append(Notification.created_at >= from_date)

        if to_date:
            to_date_end = to_date + timedelta(days=1)
            conditions.append(Notification.created_at < to_date_end)

        order_by = getattr(Notification, sort_by)
        if sort_order == "desc":
            order_by = order_by.desc()
        else:
            order_by = order_by.asc()

        notifications, total = await notification_repository.get_all_notifications(
            session=session, where_conditions=conditions, order_by=order_by, skip=skip, limit=limit
        )

        data = [self.build_notification_response(notif) for notif in notifications]

        stats = await self.get_customer_stats_quick(session, user_id)

        return {
            "data": data,
            "total": total,
            "stats": stats
        }


    async def get_customer_stats_quick(self, session: AsyncSession, user_id: str):
        base_conditions = [
            Notification.recipient_type == RecipientType.CUSTOMER,
            Notification.recipient_id == user_id
        ]
        unread_conditions = base_conditions + [Notification.is_read == False]
        unread_query = select(func.count()).select_from(Notification).where(and_(*unread_conditions))
        result_unread = await session.exec(unread_query)
        total_unread = result_unread.one() or 0

        return {
            "total_unread": total_unread,
        }




