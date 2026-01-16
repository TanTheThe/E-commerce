from src.celery_app import celery_app
from src.crud.notification.services.create_notification import CreateNotificationService
from src.database.main import async_session_maker
import asyncio
import logging

logger = logging.getLogger(__name__)

create_notification_serivce = CreateNotificationService()


@celery_app.task(name='send_return_completion_notification')
def send_return_completion_notification_task(return_order_id: str, user_id: str, order_code: str, order_id: str,
                                         stock_restored: bool):
    asyncio.run(process_send_return_completion_notification(
        return_order_id=return_order_id,
        user_id=user_id,
        order_code=order_code,
        order_id=order_id,
        stock_restored=stock_restored
    ))


async def process_send_return_completion_notification(return_order_id: str, user_id: str, order_code: str,
                                                      order_id: str, stock_restored: bool):
    async with async_session_maker() as session:
        try:
            await create_notification_serivce.create_return_completed_notification(
                session=session,
                return_order_id=return_order_id,
                customer_id=user_id,
                order_code=order_code,
                stock_restored=stock_restored,
                order_id=order_id,
            )
            await session.commit()
            logger.info(f"Sent completion notification for return order {return_order_id}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error sending notification for return order {return_order_id}: {str(e)}")
            raise

