from src.crud.brand.repositories import BrandRepository
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.material.repositories import MaterialRepository
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Categories, Color, Size, Brand, Material
from sqlmodel.ext.asyncio.session import AsyncSession
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
brand_repository = BrandRepository()
material_repository = MaterialRepository()


class GetFiltersInfoService:
    async def get_filters_info(self, category_id: str, session: AsyncSession):
        condition_parent_category = [Categories.id == category_id, Categories.deleted_at.is_(None)]
        parent_category = await categories_repository.get_category(session=session, where_conditions=condition_parent_category)
        if not parent_category:
            CategoriesException.not_found()

        condition_child_categories = [Categories.parent_id == category_id, Categories.deleted_at.is_(None)]
        child_categories, _ = await categories_repository.get_all_categories(session=session, where_conditions=condition_child_categories, skip=0, limit=1000)

        type_size = parent_category.type_size
        sizes = await size_repository.get_all_size(Size.type == type_size, session)

        colors, _ = await color_repository.get_all_color([Color.deleted_at.is_(None)], session, 0, 1000)

        brands, _ = await brand_repository.get_all_brand(session=session, where_conditions=[Brand.deleted_at.is_(None), Brand.is_active == True],
                                                         skip=0, limit=1000)

        materials, _ = await material_repository.get_all_material(
            [Material.deleted_at.is_(None), Material.is_active == True], session, 0, 1000)

        return {
            "categories": [
                {"id": str(category.id), "name": category.name, "slug": category.slug}
                for category in child_categories
            ],
            "sizes": [
                {"id": str(size.id), "name": size.name}
                for size in sizes
            ],
            "colors": [
                {"id": str(color.id), "name": color.name}
                for color in colors
            ],
            "brands": [
                {"id": str(brand.id), "name": brand.name, "slug": brand.slug}
                for brand in brands
            ],
            "materials": [
                {"id": str(material.id), "name": material.name, "slug": material.slug}
                for material in materials
            ]
        }
