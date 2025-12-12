from src.celery_app import celery_app
from src.crud.image.services.delete_image import DeleteImageService
from src.database.main import async_session_maker
import asyncio
import logging

from src.schemas.image import ImageDeleteModel

logger = logging.getLogger(__name__)

delete_image_service = DeleteImageService()


@celery_app.task(name='delete_old_image')
def delete_old_image_task(file_path: str):
    result = asyncio.run(process_delete_image(file_path))
    logger.info(f"Delete image task completed: {result}")
    return result


async def process_delete_image(file_path: str):
    async with async_session_maker() as session:
        try:
            delete_data = ImageDeleteModel(file_path=file_path)
            result = await delete_image_service.delete_image(delete_data)
            return result
        except Exception as e:
            logger.error(f"Error in delete image task: {str(e)}")
            raise e
