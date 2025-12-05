from src.crud.brand.repositories import BrandRepository
from src.database.models import Brand
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import asc, desc
from typing import Optional

brand_repository = BrandRepository()


class GetAllBrandsService:
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
