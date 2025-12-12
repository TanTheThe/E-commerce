import os
import logging
import uuid
from datetime import datetime
from fastapi import UploadFile
from src.crud.image.repositories import ImageRepository
from src.errors.image import ImageException
from src.schemas.image import UploadType, ImageUploadModel

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".svg"}

image_repository = ImageRepository()

class UploadImageService:
    def validate_file(self, file: UploadFile):
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            ImageException.file_too_large(MAX_FILE_SIZE // 1024 // 1024)

        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            ImageException.invalid_file_type(', '.join(ALLOWED_EXTENSIONS))


    def generate_unique_suffix(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"{timestamp}-{short_uuid}"


    def generate_filename(self, upload_type: UploadType, slug: str, file_extension: str, unique_suffix: str):
        if upload_type == UploadType.BRANDS:
            return f"logo-{slug}-{unique_suffix}{file_extension}"

        elif upload_type == UploadType.CATEGORIES:
            return f"{slug}-{unique_suffix}{file_extension}"

        elif upload_type == UploadType.PRODUCTS:
            return f"{slug}-{unique_suffix}{file_extension}"

        return None


    def get_folder_path(self, upload_type: UploadType) -> str:
        return upload_type.value


    async def upload_image(self, file: UploadFile, upload_data: ImageUploadModel):
        try:
            self.validate_file(file)

            file_extension = os.path.splitext(file.filename)[1].lower()

            folder = self.get_folder_path(upload_data.type)

            unique_suffix = self.generate_unique_suffix()
            filename = self.generate_filename(
                upload_data.type,
                upload_data.slug,
                file_extension,
                unique_suffix
            )

            file_path = f"{folder}/{filename}"

            file_content = await file.read()

            await image_repository.upload_file(
                file_path=file_path,
                file_content=file_content,
                content_type=file.content_type
            )

            public_url = image_repository.get_public_url(file_path)

            return {
                "url": public_url,
                "filename": filename,
                "path": file_path,
                "type": upload_data.type.value,
                "size": len(file_content),
                "content_type": file.content_type
            }

        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            ImageException.upload_failed(str(e))







































