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
        condition = and_(Brand.id == id, Brand.deleted_at.is_(None))
        existing_brand = await brand_repository.get_brand(condition, session)

        if not existing_brand:
            BrandException.brand_not_found()

        if brand_update.name and brand_update.name != existing_brand.name:
            condition_check_name = and_(Brand.name == brand_update.name, Brand.deleted_at.is_(None), Brand.id != id)
            duplicate_brand = await brand_repository.get_brand(condition_check_name, session)

            if duplicate_brand:
                BrandException.brand_name_exists()

        new_slug = None
        if brand_update.name and brand_update.name != existing_brand.name:
            base_slug = generate_slug(brand_update.name)

            new_slug = await self.generate_unique_slug_for_update(base_slug, id, session)

        try:
            condition = and_(Brand.id == id, Brand.deleted_at.is_(None))
            updated_brand_tuple = await brand_repository.update_brand(condition, brand_update, new_slug, session)

            if not updated_brand_tuple:
                BrandException.brand_update_failed()

            updated_brand = updated_brand_tuple[0]
        except Exception as e:
            await session.rollback()
            logger.error("Error create new brand: ", e)

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
        condition_slug = and_(
            Brand.slug == base_slug,
            Brand.deleted_at.is_(None),
            Brand.id != current_id
        )

        existing_slug = await brand_repository.get_brand(condition_slug, session)

        if not existing_slug:
            return base_slug

        counter = 1
        while counter <= max_attempts:
            new_slug = f"{base_slug}-{counter}"
            condition_slug = and_(
                Brand.slug == new_slug,
                Brand.deleted_at.is_(None),
                Brand.id != current_id
            )
            existing_slug = await brand_repository.get_brand(condition_slug, session)

            if not existing_slug:
                return new_slug
            counter += 1

        BrandException.cant_generate_unique_slug()

