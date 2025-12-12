from datetime import datetime
from typing import List
from src.crud.notification.repositories import NotificationRepository
from src.database.models import Notification
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.notification import RecipientType
import logging

logger = logging.getLogger(__name__)

notification_repository = NotificationRepository()

class MarkAsReadService:
    async def mark_as_read_for_admin(self, session: AsyncSession, notification_ids: List[str]):
        try:
            conditions = [
                Notification.id.in_(notification_ids),
                Notification.recipient_type == RecipientType.ADMIN,
                Notification.is_read == False
            ]
            count = await notification_repository.update_notification(
                conditions,
                {
                    "is_read": True,
                    "read_at": datetime.now()
                },
                session
            )

            failed_ids = None
            if count < len(notification_ids):
                updated, _ = await notification_repository.get_all_notifications(
                    session=session,
                    where_conditions=
                    [
                        Notification.id.in_(notification_ids),
                        Notification.is_read == True
                    ],
                )
                updated_ids = {str(n.id) for n in updated}
                failed_ids = [nid for nid in notification_ids if nid not in updated_ids]

            return {
                "count": count,
                "failed_ids": failed_ids
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to mark as read")
            raise


    async def mark_as_read_for_customer(self, session: AsyncSession, notification_ids: List[str], customer_id: str):
        try:
            conditions = [
                Notification.id.in_(notification_ids),
                Notification.recipient_type == RecipientType.CUSTOMER,
                Notification.recipient_id == customer_id,
                Notification.is_read == False
            ]

            count = await notification_repository.update_notification(
                conditions,
                {
                    "is_read": True,
                    "read_at": datetime.now()
                },
                session
            )

            failed_ids = None
            if count < len(notification_ids):
                updated, _ = await notification_repository.get_all_notifications(
                    session=session,
                    where_conditions=
                    [
                        Notification.id.in_(notification_ids),
                        Notification.recipient_id == customer_id,
                        Notification.is_read == True
                    ],
                )
                updated_ids = {str(n.id) for n in updated}
                failed_ids = [nid for nid in notification_ids if nid not in updated_ids]

            return {
                "count": count,
                "failed_ids": failed_ids
            }

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to mark as read")
            raise


    async def mark_all_as_read_for_customer(self, session: AsyncSession, customer_id: str):
        try:
            conditions = [
                Notification.recipient_type == RecipientType.CUSTOMER,
                Notification.recipient_id == customer_id,
                Notification.is_read == False
            ]

            count = await notification_repository.update_notification(
                conditions,
                {
                    "is_read": True,
                    "read_at": datetime.now()
                },
                session
            )

            return count

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to mark as read")
            raise




