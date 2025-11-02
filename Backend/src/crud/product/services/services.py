import uuid
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.product import ProductException
from src.schemas.product import DeleteMultipleProductModel

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


class ProductService:
    async def resolve_product_id(self, product_identifier: str, session: AsyncSession):
        try:
            uuid.UUID(product_identifier)
            condition = and_(Product.id == product_identifier, Product.deleted_at.is_(None))
            product = await product_repository.get_product(condition, session)
            return str(product[0].id) if product else None
        except ValueError:
            condition = and_(Product.slug == product_identifier, Product.deleted_at.is_(None))
            product = await product_repository.get_product(condition, session)
            return str(product[0].id) if product else None

    async def delete_product(self, product_id: str, session: AsyncSession):
        condition = and_(Product.id == product_id)
        product_delete = await product_repository.delete_product(condition, session)
        await session.commit()
        return product_delete

    async def delete_multiple_product(self, data: DeleteMultipleProductModel, session: AsyncSession):
        product_ids = await product_repository.delete_multiple_product(data, session)
        return product_ids

    async def count_all_products(self, session: AsyncSession):
        count_products = await product_repository.count_products(None, session)

        if count_products is None:
            ProductException.fail_count_products()

        return count_products[0]
