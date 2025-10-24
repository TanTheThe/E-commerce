from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories_Product, Categories, Product_Variant, Color
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, case
from datetime import datetime
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.product import ProductException
from src.schemas.product import ProductStatusUpdateModel, BulkUpdateStatusModel

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
size_repository = SizeRepository()
get_detail_product_service = GetDetailProductService()
product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()


class UpdateProductStatusService:
    async def update_product_status(self, product_id: str, status_data: ProductStatusUpdateModel, session: AsyncSession):
        condition = and_(Product.id == product_id, Product.deleted_at.is_(None))
        existing_product = await product_repository.get_product(condition, session)
        if not existing_product:
            ProductException.product_not_found()

        await product_repository.update_product_some_field(condition, {"status": status_data.status.value}, session)
        await session.commit() 

    async def bulk_update_product_status(self, bulk_data: BulkUpdateStatusModel, session: AsyncSession):
        product_ids = bulk_data.product_ids

        conditions = [
            Product.id.in_(product_ids),
            Product.deleted_at.is_(None)
        ]
        
        existing_products, _ = await product_repository.get_all_product(conditions, session)
        existing_ids = {str(product[0].id) for product in existing_products}
        
        not_found_ids = [str(pid) for pid in product_ids if pid not in existing_ids]

        if not_found_ids:
            ProductException.invalid_product_ids()
        
        condition = Product.id.in_(product_ids)
        await product_repository.update_product_some_field(
            condition,
            {"status": bulk_data.status, "updated_at": datetime.now()},
            session
        )

        await session.commit()
        
        
