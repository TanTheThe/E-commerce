import logging
from datetime import datetime
from src.crud.image.repositories import ImageRepository
from src.errors.image import ImageException
from src.schemas.image import ImageDeleteModel

logger = logging.getLogger(__name__)

image_repository = ImageRepository()

class DeleteImageService:
    async def delete_image(self, delete_data: ImageDeleteModel):
        try:
            # exists = await image_repository.check_file_exists(delete_data.file_path)
            # if not exists:
            #     ImageException.file_not_found(delete_data.file_path)

            await image_repository.delete_file(delete_data.file_path)

            return {
                "deleted_path": delete_data.file_path,
                "deleted_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")
            ImageException.delete_failed(str(e))







































