from src.crud.brand.repositories import BrandRepository
from src.database.models import Brand
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.brand import BrandException
from src.schemas.brand import BrandCreateModel
from src.crud.brand.utils import generate_slug
import logging

brand_repository = BrandRepository()
logger = logging.getLogger(__name__)


class CreateBrandService:
    async def create_brand(self, brand_data: BrandCreateModel, session: AsyncSession):
        if not brand_data.name or not brand_data.name.strip():
            BrandException.invalid_brand_name()

        if len(brand_data.name.strip()) > 255:
            raise BrandException.name_too_long()

        if brand_data.logo and len(brand_data.logo.strip()) > 500:
            raise BrandException.invalid_logo_url()

        condition = [Brand.name == brand_data.name, Brand.deleted_at.is_(None)]
        existing_brand = await brand_repository.get_brand(session=session, where_conditions=condition)

        if existing_brand:
            BrandException.brand_name_exists()

        slug = generate_slug(brand_data.name)
        slug = await self.generate_unique_slug(slug, session)

        new_brand_dict = {
            "name": brand_data.name,
            "slug": slug,
            "logo": brand_data.logo,
            "is_active": brand_data.is_active
        }

        try:
            brand = await brand_repository.create_brand(new_brand_dict, session)
            await session.commit()
            await session.refresh(brand)
        except Exception as e:
            await session.rollback()
            logger.error("Error create new brand: ", e)

        return {
            "id": str(brand.id),
            "name": brand.name,
            "slug": brand.slug,
            "logo": brand.logo,
            "is_active": brand.is_active,
            "created_at": str(brand.created_at) if brand.created_at else None
        }

    async def generate_unique_slug(self, base_slug: str, session: AsyncSession, force_new: bool = False) -> str:
        if not force_new:
            condition_slug = [Brand.slug == base_slug, Brand.deleted_at.is_(None)]
            existing_slug = await brand_repository.get_brand(session=session, where_conditions=condition_slug)
            if not existing_slug:
                return base_slug

        counter = 1
        while True:
            new_slug = f"{base_slug}-{counter}"
            condition_slug = [Brand.slug == new_slug, Brand.deleted_at.is_(None)]
            existing_slug = await brand_repository.get_brand(session=session, where_conditions=condition_slug)
            if not existing_slug:
                return new_slug
            counter += 1
