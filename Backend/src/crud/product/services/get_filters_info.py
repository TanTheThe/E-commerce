from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Categories, Color, Size
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.categories import CategoriesException

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


class GetFiltersInfoService:
    async def get_filters_info(self, category_id: str, session: AsyncSession):
        condition_parent_category = and_(Categories.id == category_id, Categories.deleted_at.is_(None))
        parent_category = await categories_repository.get_category(condition_parent_category, session)
        if not parent_category:
            CategoriesException.not_found()

        condition_child_categories = [Categories.parent_id == category_id, Categories.deleted_at.is_(None)]
        child_categories, _ = await categories_repository.get_all_categories(condition_child_categories, session, 0, 1000,)

        type_size = parent_category.type_size
        sizes = await size_repository.get_all_size(Size.type == type_size, session)

        colors, _ = await color_repository.get_all_color([Color.deleted_at.is_(None)], session, 0, 1000)

        return {
            "categories": [
                {"id": str(category.id), "name": category.name}
                for category in child_categories
            ],
            "sizes": [
                {"id": str(size.id), "name": size.name}
                for size in sizes
            ],
            "colors": [
                {"id": str(color.id), "name": color.name}
                for color in colors
            ]
        }
