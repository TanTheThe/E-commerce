from src.celery_app import celery_app
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.return_order.services.retry_refund_service import RetryRefundService
from src.database.main import async_session_maker
import asyncio
import logging
from src.schemas.return_order import RefundRetrySource

logger = logging.getLogger(__name__)

return_order_repository = ReturnOrderRepository()
retry_refund_service = RetryRefundService()


@celery_app.task(name='retry_failed_refund')
def retry_failed_refund_task(refund_id: str):
    asyncio.run(process_retry_failed_refund(refund_id))

async def process_retry_failed_refund(refund_id: str):
    async with async_session_maker() as session:
        try:
            logger.info(f"Auto-retrying refund {refund_id}")

            result = await retry_refund_service.retry_refund_payment(
                refund_id=refund_id,
                request=None,
                session=session,
                source=RefundRetrySource.AUTO
            )

            if result["status"] == "success":
                logger.info(f"Auto-retry succeeded for refund {refund_id}")
            elif result["status"] == "manual_required":
                logger.warning(f"Refund {refund_id} requires manual intervention")
            else:
                logger.info(f"Auto-retry failed for refund {refund_id}, will retry later")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error auto-retrying refund {refund_id}: {str(e)}")
            raise