from src.database.models import Categories
from src.schemas.categories import CategoriesCreateModel, CategoriesUpdateModel, CategoriesFilterModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.crud.categories.repositories import CategoriesRepository
from src.errors.categories import CategoriesException

categories_repository = CategoriesRepository()


class CategoriesService:
    async def create_categories_service(self, categories_data: CategoriesCreateModel, session: AsyncSession):
        new_categories = await categories_repository.create_categories(categories_data, session)

        new_categories_dict = {
            "id": str(new_categories.id),
            "name": new_categories.name,
            "image": new_categories.image,
            "parent_id": str(new_categories.parent_id) if new_categories.parent_id else None,
        }

        return new_categories_dict

    async def get_all_categories_service(self, filter_data: CategoriesFilterModel, session: AsyncSession, skip: int = 0,
                                         limit: int = 10):
        filters = [Categories.deleted_at.is_(None)]
        if filter_data.search:
            filters.append(Categories.name.ilike(f"%{filter_data.search}%"))

        categories, total = await categories_repository.get_all_categories(filters, session, skip, limit)

        if len(categories) == 0:
            CategoriesException.empty_list()

        return {
            "data": [
                {
                    "id": str(cat.id),
                    "name": cat.name,
                    "image": cat.image,
                    "parent_id": str(cat.parent_id) if cat.parent_id else None
                }
                for cat in categories
            ],
            "total": total
        }

    async def update_categories_service(self, id: str, categories_update: CategoriesUpdateModel, session: AsyncSession):
        condition = and_(Categories.id == id)
        category = await categories_repository.get_category(condition, session)

        if not category:
            CategoriesException.not_found()

        update_data = categories_update.model_dump(exclude_unset=True)

        if 'parent_id' in update_data and update_data['parent_id']:
            parent_id = update_data['parent_id']
            if str(parent_id) == id:
                CategoriesException.invalid_parent()

            parent = await categories_repository.get_category(Categories.id == parent_id, session)
            if not parent:
                CategoriesException.parent_not_found()

        await categories_repository.update_categories(category, update_data, session)
        await session.commit()
        await session.refresh(category)

        response_dict = {
            "id": str(category.id),
            "name": category.name,
            "image": category.image,
            "parent_id": str(category.parent_id) if category.parent_id else None
        }

        return response_dict

    async def delete_categories_service(self, id: str, session: AsyncSession):
        condition = and_(Categories.id == id, Categories.deleted_at.is_(None))
        await categories_repository.delete_categories(condition, session)

        sub_categories_condition = and_(Categories.parent_id == id, Categories.deleted_at.is_(None))
        await categories_repository.delete_sub_categories(sub_categories_condition, session)

        await session.commit()
        return {}
