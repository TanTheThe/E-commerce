from src.celery_tasks.delete_image import delete_old_image_task
from src.crud.brand.repositories import BrandRepository
from src.database.models import Brand
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.brand import DeleteMultipleBrandsModel
import logging

brand_repository = BrandRepository()

logger = logging.getLogger(__name__)


class DeleteBrandService:
    async def delete_brand(self, brand_id: str, session: AsyncSession):
        condition = [Brand.id == brand_id, Brand.deleted_at.is_(None)]
        brand_to_delete = await brand_repository.get_brand(
            session=session,
            where_conditions=condition
        )
        if brand_to_delete and brand_to_delete.logo:
            old_logo = brand_to_delete.logo
        else:
            old_logo = None

        deleted_id = await brand_repository.delete_brand(condition, session)

        if old_logo:
            delete_old_image_task.apply_async(
                args=[old_logo],
                countdown=300
            )
            logger.info(f"Scheduled deletion of logo for brand {brand_id}: {old_logo}")

        return deleted_id


    async def delete_multiple_brands(self, data: DeleteMultipleBrandsModel, session: AsyncSession):
        conditions = [Brand.id.in_(data.brand_ids), Brand.deleted_at.is_(None)]
        brands_to_delete, _ = await brand_repository.get_all_brand(
            session=session,
            where_conditions=conditions
        )

        logos_to_delete = [
            brand.logo for brand in brands_to_delete
            if brand.logo
        ]

        brand_ids = await brand_repository.delete_multiple_brand(data, session)

        for logo in logos_to_delete:
            delete_old_image_task.apply_async(
                args=[logo],
                countdown=300
            )

        if logos_to_delete:
            logger.info(f"Scheduled deletion of {len(logos_to_delete)} logos for brands: {brand_ids}")

        return brand_ids
