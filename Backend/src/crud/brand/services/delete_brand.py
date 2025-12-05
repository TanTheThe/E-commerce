from src.crud.brand.repositories import BrandRepository
from src.database.models import Brand
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.schemas.brand import DeleteMultipleBrandsModel

brand_repository = BrandRepository()


class DeleteBrandService:
    async def delete_brand(self, brand_id: str, session: AsyncSession):
        condition = and_(Brand.id == brand_id, Brand.deleted_at.is_(None))
        return await brand_repository.delete_brand(condition, session)

    async def delete_multiple_brands(self, data: DeleteMultipleBrandsModel, session: AsyncSession):
        brand_ids = await brand_repository.delete_multiple_brand(data, session)
        return brand_ids
