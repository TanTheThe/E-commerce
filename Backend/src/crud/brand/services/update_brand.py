from src.celery_tasks.delete_image import delete_old_image_task
from src.crud.brand.repositories import BrandRepository
from src.database.models import Brand
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.brand import BrandException
from src.schemas.brand import BrandUpdateModel
from src.crud.brand.utils import generate_slug
import logging

brand_repository = BrandRepository()
logger = logging.getLogger(__name__)

class UpdateBrandService:
    async def update_brand(self, id: str, brand_update: BrandUpdateModel, session: AsyncSession):
        condition = [Brand.id == id, Brand.deleted_at.is_(None)]
        existing_brand = await brand_repository.get_brand(session=session, where_conditions=condition)
        if not existing_brand:
            BrandException.brand_not_found()

        old_logo = existing_brand.logo if existing_brand.logo else None

        if brand_update.name and brand_update.name != existing_brand.name:
            condition_check_name = [Brand.name == brand_update.name, Brand.deleted_at.is_(None), Brand.id != id]
            duplicate_brand = await brand_repository.get_brand(session=session, where_conditions=condition_check_name)
            if duplicate_brand:
                BrandException.brand_name_exists()

        new_slug = None
        if brand_update.name and brand_update.name != existing_brand.name:
            base_slug = generate_slug(brand_update.name)
            new_slug = await self.generate_unique_slug_for_update(base_slug, id, session)

        updated_brand = None
        try:
            condition = and_(Brand.id == id, Brand.deleted_at.is_(None))

            update_data = brand_update.model_dump(exclude_unset=False)

            updated_brand_tuple = await brand_repository.update_brand(condition, update_data, new_slug, session)
            updated_brand = updated_brand_tuple[0]

            if not updated_brand_tuple:
                BrandException.brand_update_failed()

            await session.commit()
            await session.refresh(updated_brand)

            if brand_update.logo and old_logo and brand_update.logo != old_logo:
                delete_old_image_task.apply_async(
                    args=[old_logo],
                    countdown=300  # 5 phút
                )
                logger.info(f"Scheduled deletion of old logo: {old_logo}")

        except Exception as e:
            await session.rollback()
            logger.error("Error create new brand: ", e)
            raise e

        return {
            "id": str(updated_brand.id),
            "name": updated_brand.name,
            "slug": updated_brand.slug,
            "logo": updated_brand.logo,
            "is_active": updated_brand.is_active,
            "updated_at": str(updated_brand.updated_at) if updated_brand.updated_at else None
        }


    async def generate_unique_slug_for_update(self, base_slug: str, current_id: str, session: AsyncSession,
                                              max_attempts: int = 100):
        condition_slug = [
            Brand.slug == base_slug,
            Brand.deleted_at.is_(None),
            Brand.id != current_id
        ]

        existing_slug = await brand_repository.get_brand(session=session, where_conditions=condition_slug)

        if not existing_slug:
            return base_slug

        counter = 1
        while counter <= max_attempts:
            new_slug = f"{base_slug}-{counter}"
            condition_slug = [
                Brand.slug == new_slug,
                Brand.deleted_at.is_(None),
                Brand.id != current_id
            ]
            existing_slug = await brand_repository.get_brand(session=session, where_conditions=condition_slug)

            if not existing_slug:
                return new_slug
            counter += 1

        BrandException.cant_generate_unique_slug()

