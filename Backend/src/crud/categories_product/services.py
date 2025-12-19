from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.database.models import Categories_Product
from src.errors.categories import CategoriesException
from src.errors.product import ProductException
from src.database.models import Categories
import logging


logger = logging.getLogger(__name__)

categories_product_repository = CategoriesProductRepository()
categories_repository = CategoriesRepository()

class CategoriesProductService:
    async def update_categories_product(self, product_id: str, new_category_ids: List[str], session: AsyncSession):
        try:
            if not new_category_ids:
                raise ProductException.categories_required()

            if len(new_category_ids) > 5:
                raise ProductException.too_many_categories()

            if len(set(new_category_ids)) != len(new_category_ids):
                raise CategoriesException.duplicate_categories()

            condition = [
                Categories.id.in_(new_category_ids),
                Categories.deleted_at.is_(None),
                Categories.is_active == True
            ]

            valid_categories, total = await categories_repository.get_all_categories(
                session=session,
                where_conditions=condition,
                skip=0,
                limit=len(new_category_ids)
            )

            found_ids = {cat.id for cat in valid_categories}
            missing_ids = set(new_category_ids) - found_ids

            if missing_ids:
                raise CategoriesException.not_found()

            condition = and_(Categories_Product.product_id == product_id)
            await categories_product_repository.delete_cate_product(condition, session)

            await categories_product_repository.create_cate_product(valid_categories, product_id, session)

        except Exception as e:
            logger.error(f"Error updating categories for product {product_id}: {str(e)}")
            raise ProductException.update_failed()








