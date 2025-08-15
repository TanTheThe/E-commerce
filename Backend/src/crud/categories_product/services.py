from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_

from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.database.models import Categories_Product
from src.schemas.categories_product import CategoriesCreateModel
from src.database.models import Categories

categories_product_repository = CategoriesProductRepository()
categories_repository = CategoriesRepository()

class CategoriesProductService:
    async def update_categories_product(self, product_id: str, new_category_ids: list, session: AsyncSession):
        condition = and_(Categories_Product.product_id == product_id)
        await categories_product_repository.delete_cate_product(condition, session)

        condition = Categories.id.in_(new_category_ids)
        valid_categories, total = await categories_repository.get_all_categories([condition], session)
        valid_categories = [cat for cat in valid_categories if cat.deleted_at is None]

        await categories_product_repository.create_cate_product(valid_categories, product_id, session)








