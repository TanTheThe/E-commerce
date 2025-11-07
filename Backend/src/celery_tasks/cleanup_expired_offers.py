from src.celery_app import celery_app
from src.crud.special_offer.services.cleanup_expired_offers import OfferCleanupService
from src.database.main import async_session_maker
import asyncio
import logging

logger = logging.getLogger(__name__)

offer_cleanup_service = OfferCleanupService()


@celery_app.task(name='cleanup_expired_offers')
def cleanup_expired_offers_task():
    result = asyncio.run(process_cleanup_expired_offers())
    logger.info(f"Cleanup task completed: {result}")
    return result

async def process_cleanup_expired_offers():
    async with async_session_maker() as session:
        try:
            result = await offer_cleanup_service.cleanup_expired_offers(session)
            return result
        except Exception as e:
            logger.error(f"Error in cleanup task: {str(e)}")