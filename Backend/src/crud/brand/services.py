from src.crud.brand.repositories import BrandRepository
from src.database.models import Brand, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, asc, desc
from src.errors.brand import BrandException
from src.schemas.brand import BrandCreateModel, BrandUpdateModel, DeleteMultipleBrandsModel
from src.crud.brand.utils import generate_slug
from typing import Optional

brand_repository = BrandRepository()


class BrandService:
    async def create_brand_service(self, brand_data: BrandCreateModel, session: AsyncSession):
        condition = and_(Brand.name == brand_data.name, Brand.deleted_at.is_(None))
        existing_brand = await brand_repository.get_brand(condition, session)

        if existing_brand:
            BrandException.brand_name_exists()

        slug = generate_slug(brand_data.name)
        slug = await self._generate_unique_slug(slug, session)

        new_brand_dict = {
            "name": brand_data.name,
            "slug": slug,
            "logo": brand_data.logo,
            "is_active": brand_data.is_active
        }

        brand = await brand_repository.create_brand(new_brand_dict, session)

        await session.commit()
        await session.refresh(brand)

        return {
            "id": str(brand.id),
            "name": brand.name,
            "slug": brand.slug,
            "logo": brand.logo,
            "is_active": brand.is_active,
            "created_at": str(brand.created_at) if brand.created_at else None
        }

    async def _generate_unique_slug(self, base_slug: str, session: AsyncSession, force_new: bool = False) -> str:
        if not force_new:
            condition_slug = and_(Brand.slug == base_slug, Brand.deleted_at.is_(None))
            existing_slug = await brand_repository.get_brand(condition_slug, session)
            if not existing_slug:
                return base_slug

        counter = 1
        while True:
            new_slug = f"{base_slug}-{counter}"
            condition_slug = and_(Brand.slug == new_slug, Brand.deleted_at.is_(None))
            existing_slug = await brand_repository.get_brand(condition_slug, session)
            if not existing_slug:
                return new_slug
            counter += 1

    async def get_all_brands_admin(self, search: Optional[str], is_active: Optional[bool],
                                   sort_by: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = [Brand.deleted_at.is_(None)]

        if search:
            conditions.append(Brand.name.ilike(f"%{search}%"))

        if is_active is not None:
            conditions.append(Brand.is_active == is_active)

        order_by_clause = None

        if sort_by == "name_asc":
            order_by_clause = asc(Brand.name)
        elif sort_by == "name_desc":
            order_by_clause = desc(Brand.name)
        elif sort_by == "created_asc":
            order_by_clause = asc(Brand.created_at)
        else:
            order_by_clause = desc(Brand.created_at)

        brands, total = await brand_repository.get_all_brand(session=session, where_conditions=conditions, skip=skip, limit=limit,
                                                             order_by=order_by_clause)

        brand_list = []
        for brand in brands:
            brand_dict = {
                "id": str(brand.id),
                "name": brand.name,
                "slug": brand.slug,
                "logo": brand.logo,
                "is_active": brand.is_active,
                "product_count": brand.products_count,
                "created_at": str(brand.created_at) if brand.created_at else None
            }
            brand_list.append(brand_dict)

        return {
            "data": brand_list,
            "total": total
        }

    async def get_all_brands_customer(self, search: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = [Brand.deleted_at.is_(None)]

        if search:
            conditions.append(Brand.name.ilike(f"%{search}%"))

        brands, total = await brand_repository.get_all_brand(session=session, where_conditions=conditions, skip=skip, limit=limit)

        brand_list = []
        for brand in brands:
            brand_dict = {
                "id": str(brand.id),
                "name": brand.name,
                "slug": brand.slug,
                "logo": brand.logo,
                "is_active": brand.is_active,
                "product_count": brand.products_count,
            }
            brand_list.append(brand_dict)

        return {
            "data": brands,
            "total": total
        }

    async def update_brand_service(self, id: str, brand_update: BrandUpdateModel, session: AsyncSession):
        condition = and_(Brand.id == id, Brand.deleted_at.is_(None))
        existing_brand = await brand_repository.get_brand(condition, session)

        if not existing_brand:
            BrandException.brand_not_found()

        if brand_update.name and brand_update.name != existing_brand.name:
            condition_check_name = and_(Brand.name == brand_update.name, Brand.deleted_at.is_(None))
            duplicate_brand = await brand_repository.get_brand(condition_check_name, session)

            if duplicate_brand:
                BrandException.brand_name_exists()

        new_slug = None
        if brand_update.name and brand_update.name != existing_brand.name:
            new_slug = generate_slug(brand_update.name)
            condition_slug_1 = and_(Brand.slug == new_slug, Brand.deleted_at.is_(None))
            existing_slug = await brand_repository.get_brand(condition_slug_1, session)
            if existing_slug and str(existing_slug.id) != id:
                counter = 1
                temp_slug = ""
                while existing_slug:
                    temp_slug = f"{new_slug}-{counter}"
                    condition_slug_2 = and_(Brand.slug == temp_slug, Brand.deleted_at.is_(None))
                    existing_slug = await brand_repository.get_brand(condition_slug_2, session)
                    if not existing_slug or str(existing_slug.id) == id:
                        break
                    counter += 1
                new_slug = temp_slug

        condition = and_(Brand.id == id)
        updated_brand_tuple = await brand_repository.update_brand(condition, brand_update, new_slug, session)

        updated_brand = updated_brand_tuple[0]

        return {
            "id": str(updated_brand.id),
            "name": updated_brand.name,
            "slug": updated_brand.slug,
            "logo": updated_brand.logo,
            "is_active": updated_brand.is_active,
            "updated_at": str(updated_brand.updated_at) if updated_brand.updated_at else None
        }

    async def delete_brand(self, brand_id: str, session: AsyncSession):
        condition = and_(Brand.id == brand_id, Brand.deleted_at.is_(None))
        return await brand_repository.delete_brand(condition, session)

    async def delete_multiple_brands(self, data: DeleteMultipleBrandsModel, session: AsyncSession):
        brand_ids = await brand_repository.delete_multiple_brand(data, session)
        return brand_ids
