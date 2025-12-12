from src.celery_app import celery_app
from src.crud.image.services.delete_image import DeleteImageService
from src.database.main import async_session_maker
import asyncio
import logging

from src.schemas.image import ImageDeleteModel

logger = logging.getLogger(__name__)

delete_image_service = DeleteImageService()


@celery_app.task(name='delete_multiple_images')
def delete_multiple_images_task(file_paths: list):
    result = asyncio.run(process_delete_multiple_images(file_paths))
    logger.info(f"Delete multiple images task completed: {result}")
    return result


async def process_delete_multiple_images(file_paths: list):
    async with async_session_maker() as session:
        results = []
        failed = []

        for file_path in file_paths:
            try:
                delete_data = ImageDeleteModel(file_path=file_path)
                result = await delete_image_service.delete_image(delete_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Error deleting image {file_path}: {str(e)}")
                failed.append({"file_path": file_path, "error": str(e)})

        return {
            "deleted": results,
            "failed": failed,
            "total": len(file_paths)
        }
