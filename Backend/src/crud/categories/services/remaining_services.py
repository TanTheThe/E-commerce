import uuid
from src.crud.size.services import SizeService
from src.database.models import Categories
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.categories.repositories import CategoriesRepository
from src.errors.categories import CategoriesException

categories_repository = CategoriesRepository()
size_service = SizeService()

class RemainingCategoriesService:
    async def resolve_category_id(self, category_identifier: str, session: AsyncSession):
        try:
            uuid.UUID(category_identifier)
            condition = [Categories.id == category_identifier, Categories.deleted_at.is_(None)]
            category = await categories_repository.get_category(session=session, where_conditions=condition)
            return str(category.id) if category else None
        except ValueError:
            condition = [Categories.slug == category_identifier, Categories.deleted_at.is_(None)]
            category = await categories_repository.get_category(session=session, where_conditions=condition)
            return str(category.id) if category else None


    async def get_detail_category_service(self, id: str, session: AsyncSession):
        condition = [Categories.id == id]
        categories = await categories_repository.get_category(session=session, where_conditions=condition)

        if categories is None:
            CategoriesException.not_found()

        return {
            "id": str(categories.id),
            "name": categories.name,
            "image": categories.image,
            "parent_id": str(categories.parent_id) if categories.parent_id else None,
            "type_size": categories.type_size
        }

    async def get_categories_select_box_service(self, session: AsyncSession):
        condition = [
            Categories.parent_id.isnot(None),
            Categories.deleted_at.is_(None)
        ]

        categories, _ = await categories_repository.get_all_categories(session=session, where_conditions=condition, skip=0, limit=1000)

        return [
            {
                "id": str(category.id),
                "name": category.name
            }
            for category in categories
        ]

    async def delete_categories_service(self, id: str, session: AsyncSession):
        condition = [Categories.id == id, Categories.deleted_at.is_(None)]
        await categories_repository.delete_categories(condition, session)

        sub_categories_condition = [Categories.parent_id == id, Categories.deleted_at.is_(None)]
        await categories_repository.delete_sub_categories(sub_categories_condition, session)

        await session.commit()
        return {}
