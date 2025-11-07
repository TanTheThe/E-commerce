from src.celery_app import celery_app
from src.crud.special_offer.services.cleanup_expired_offers import OfferCleanupService
from src.database.main import async_session_maker
import asyncio
import logging

logger = logging.getLogger(__name__)

offer_cleanup_service = OfferCleanupService()


@celery_app.task(name='auto_complete_return_order')
def auto_complete_return_order_task(return_order_id: str):
    result = asyncio.run(process_auto_complete_return(return_order_id))
    logger.info(f"Auto-complete task completed: {result}")
    return result

async def process_auto_complete_return(return_order_id: str):
    async with async_session_maker() as session:
        try:
            result = await auto_complete_return_service.auto_complete_return(return_order_id, session)
            return result
        except Exception as e:
            logger.error(f"Error in auto-complete return task: {str(e)}")