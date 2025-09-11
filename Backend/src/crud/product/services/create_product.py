from src.crud.color.repositories import ColorRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Categories, Color
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.errors.color import ColorException
from src.errors.product import ProductException
from src.errors.categories import CategoriesException

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()


class CreateProductService:
    async def create_product(self, product_data, session: AsyncSession):
        if not product_data.name:
            ProductException.invalid_name()

        if not product_data.images:
            ProductException.invalid_images()

        if not product_data.categories_id:
            ProductException.invalid_categories()

        if not product_data.product_variant:
            ProductException.invalid_variant()

        try:
            category_ids = product_data.categories_id
            condition = [Categories.id.in_(category_ids), Categories.deleted_at.is_(None)]
            existing_categories, total = await categories_repository.get_all_categories(condition, session, 0, 1000)

            existing_ids = {c.id for c in existing_categories}
            missing_ids = set(category_ids) - existing_ids
            if missing_ids:
                CategoriesException.categories_not_exist()

            color_ids = []
            for variant in product_data.product_variant:
                if variant.color_id:
                    if variant.color_name or variant.color_code:
                        ColorException.invalid_color_format()
                    color_ids.append(variant.color_id)
                elif variant.color_name and variant.color_code:
                    pass
                else:
                    ColorException.invalid_color_format()

            if color_ids:
                condition = [Color.id.in_(color_ids), Color.deleted_at.is_(None)]
                existing_colors, _ = await color_repository.get_all_color(condition, session, 0, 1000)
                existing_color_ids = {str(c.id) for c in existing_colors}
                missing_color_ids = set(color_ids) - existing_color_ids
                if missing_color_ids:
                    ColorException.color_not_exists()

            new_product = await product_repository.create_product(product_data, session)

            await cate_product_repository.create_cate_product(existing_categories, new_product.id, session)

            await product_variant_repository.create_product_variant(product_data.product_variant, new_product.id,
                                                                    session)

            await session.commit()
            await session.refresh(new_product)

            product_dict = {
                "id": str(new_product.id),
                "name": new_product.name,
                "images": new_product.images,
                "description": new_product.description,
                "short_description": new_product.short_description,
                "created_at": str(new_product.created_at),
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                        "parent_id": str(category.parent_id) if category.parent_id else None
                    } for category in existing_categories
                ],
                "status": new_product.status,
                "product_variant": [item.dict() for item in product_data.product_variant]
            }

            return product_dict
        except:
            await session.rollback()
            ProductException.invalid_create_product()
