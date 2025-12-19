from typing import List, Optional
from src.celery_app import celery_app
from src.crud.notification.services.create_notification import CreateNotificationService
from src.database.main import async_session_maker
import asyncio
import logging

logger = logging.getLogger(__name__)

create_notification_serivce = CreateNotificationService()


@celery_app.task(name='send_assign_offer_notifications')
def send_assign_offer_notifications_task(special_offer_id: str, special_offer_name: str, user_ids: List[str],
                                         admin_note: Optional[str] = None):
    result = asyncio.run(process_send_notifications(
        special_offer_id=special_offer_id,
        special_offer_name=special_offer_name,
        user_ids=user_ids,
        admin_note=admin_note
    ))
    logger.info(f"Send assign offer notifications task completed: {result}")
    return result


async def process_send_notifications(special_offer_id: str, special_offer_name: str, user_ids: List[str],
                                     admin_note: Optional[str]):
    async with async_session_maker() as session:
        BATCH_SIZE = 50
        total_sent = 0
        failed_count = 0

        for i in range(0, len(user_ids), BATCH_SIZE):
            batch = user_ids[i:i + BATCH_SIZE]

            try:
                await create_notification_serivce.bulk_create_assign_special_offer_notification(
                    session=session,
                    special_offer_id=special_offer_id,
                    special_offer_name=special_offer_name,
                    customer_ids=batch,
                    admin_note=admin_note
                )

                await session.commit()
                total_sent += len(batch)

            except Exception as e:
                failed_count += len(batch)
                logger.error(
                    f"Failed to send batch {i // BATCH_SIZE + 1} for offer {special_offer_id}: "
                    f"{str(e)}"
                )
                await session.rollback()

        result = {
            "total_sent": total_sent,
            "failed_count": failed_count,
            "special_offer_id": special_offer_id
        }

        return result