from sqlalchemy.orm import noload
from src.crud.brand.repositories import BrandRepository
from src.database.models import Brand, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, or_, asc, desc
from src.errors.brand import BrandException
from src.schemas.brand import BrandCreateModel, BrandUpdateModel, DeleteMultipleBrandsModel
from src.crud.brand.utils import generate_slug
from typing import Optional

brand_repository = BrandRepository()

class BrandService:
    async def create_brand_service(self, brand_data: BrandCreateModel, session: AsyncSession):
        condition = and_(Brand.name == brand_data.name)
        existing_brand = await brand_repository.get_brand(condition, session)
        
        if existing_brand:
            BrandException.brand_name_exists()
            
        slug = generate_slug(brand_data.name)
        
        condition_slug = and_(Brand.slug == slug, Brand.deleted_at.is_(None))
        existing_slug = await brand_repository.get_brand(condition_slug, session)
        if existing_slug:
            counter = 1
            while existing_slug:
                new_slug = f"{slug}-{counter}"
                condition_slug = and_(Brand.slug == new_slug, Brand.deleted_at.is_(None))
                existing_slug = await brand_repository.get_brand(condition_slug, session)
                counter += 1
            slug = new_slug
            
        new_brand_dict = {
            "name": brand_data.name,
            "slug": slug,
            "logo": brand_data.logo,
            "is_active": brand_data.is_active
        }
        
        brand = await brand_repository.create_brand(new_brand_dict, session)

        await session.commit()

        return {
            "id": str(brand.id),
            "name": brand.name,
            "slug": brand.slug,
            "logo": brand.logo,
            "is_active": brand.is_active,
            "created_at": str(brand.created_at) if brand.created_at else None
        }

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

        brands, total = await brand_repository.get_all_brand(conditions, session, skip, limit, order_by_clause=order_by_clause)

        brand_list = []
        for brand in brands:
            condition = and_(Product.brand_id == brand.id, Product.deleted_at.is_(None))
            product_count = await brand_repository.count_products_by_brand(condition, session)
            brand_dict = {
                "id": str(brand.id),
                "name": brand.name,
                "slug": brand.slug,
                "logo": brand.logo,
                "is_active": brand.is_active,
                "product_count": product_count,
                "created_at": str(brand.created_at) if brand.created_at else None
            }
            brand_list.append(brand_dict)
        
        return {
            "data": brands,
            "total": total
        }
        
    
    async def get_all_brands_customer(self, search: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = [Brand.deleted_at.is_(None)]
        
        if search:
            conditions.append(Brand.name.ilike(f"%{search}%"))

        brands, total = await brand_repository.get_all_brand(conditions, session, skip, limit)

        brand_list = []
        for brand in brands:
            condition = and_(Product.brand_id == brand.id, Product.deleted_at.is_(None))
            product_count = await brand_repository.count_products_by_brand(condition, session)
            brand_dict = {
                "id": str(brand.id),
                "name": brand.name,
                "slug": brand.slug,
                "logo": brand.logo,
                "is_active": brand.is_active,
                "product_count": product_count,
            }
            brand_list.append(brand_dict)
        
        return {
            "data": brands,
            "total": total
        }
        
        
    async def get_popular_brands(self, limit: int, session: AsyncSession):
        brands = await self.brand_repo.get_popular_brands(limit, session)
        
        brand_list = []
        for brand in brands:
            brand_dict = {
                "id": str(brand.id),
                "name": brand.name,
                "slug": brand.slug,
                "logo": brand.logo,
                "product_count": brand.product_count
            }
            brand_list.append(brand_dict)
        
        return {"data": brand_list}
    

    async def update_brand_service(self, id: str, brand_update: BrandUpdateModel, session: AsyncSession):
        condition = and_(Brand.id == id, Brand.deleted_at.is_(None))
        brand = await brand_repository.get_brand(condition, session)

        if not brand:
            BrandException.brand_not_found()
            
        update_data = brand_update.dict(exclude_none=True)

        if update_data:
            await brand_repository.update_brand(condition, update_data, session)
            await session.commit()

        brand_dict = {
            "id": str(brand.id),
            "name": update_data.get("name", brand.name),
            "logo": update_data.get("logo", brand.logo),
            "is_active": update_data.get("is_active", brand.is_active),
        }

        return brand_dict


    async def delete_brand(self, brand_id: str, session: AsyncSession):
        condition = and_(Brand.id == brand_id)
        return await brand_repository.delete_brand(condition, session)
    
    async def delete_multiple_brand(self, data: DeleteMultipleBrandsModel, session: AsyncSession):
        brand_ids = await brand_repository.delete_multiple_brand(data, session)
        return brand_ids