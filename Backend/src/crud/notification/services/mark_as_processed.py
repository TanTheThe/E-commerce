from datetime import datetime
from typing import Optional

from src.crud.notification.repositories import NotificationRepository
from src.database.models import Notification
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.notification import NotificationException
import logging
import json
from src.schemas.notification import RecipientType

logger = logging.getLogger(__name__)

notification_repository = NotificationRepository()

class MarkAsProcessedService:
    async def mark_as_processed(self, session: AsyncSession, notification_id: str, processed_by_id: Optional[str] = None,
                                processed_by_email: Optional[str] = None):
        try:
            conditions = [
                Notification.id == notification_id,
                Notification.recipient_type == RecipientType.ADMIN
            ]
            notification = await notification_repository.get_notification(session=session, where_conditions=conditions)

            if not notification:
                NotificationException.notification_not_found()

            if not notification.action_type:
                NotificationException.notification_not_require_process()

            if notification.is_processed:
                NotificationException.notification_previously_processed()

            notification.is_processed = True
            notification.processed_at = datetime.now()

            if notification.action_data:
                action_data = json.loads(notification.action_data) if isinstance(notification.action_data,
                                                                                 str) else notification.action_data
                action_data['processed_by_id'] = processed_by_id
                action_data['processed_by_email'] = processed_by_email
                notification.action_data = json.dumps(action_data)

            session.add(notification)
            await session.commit()
            await session.refresh(notification)

            return {
                "notification_id": str(notification.id),
                "processed_at": datetime.now().isoformat(),
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to mark as processed")
            raise




