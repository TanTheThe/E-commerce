from src.database.models import Categories
from src.schemas.categories import CategoriesCreateModel, CategoriesUpdateModel, CategoriesFilterModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, select, func, or_
from sqlalchemy.orm import aliased
from src.crud.categories.repositories import CategoriesRepository
from src.errors.categories import CategoriesException
import time

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
                                         limit: int = 5):
        if filter_data.search:
            search_filter = [Categories.deleted_at.is_(None), Categories.name.ilike(f"%{filter_data.search}%")]
            matched_categories, _ = await categories_repository.get_all_categories(search_filter, session, 0, 1000)

            matched_parents = [cat for cat in matched_categories if cat.parent_id is None]
            matched_children = [cat for cat in matched_categories if cat.parent_id is not None]

            additional_parent_ids = {cat.parent_id for cat in matched_children if cat.parent_id} - {p.id for p in matched_parents}
            additional_parents = []
            if additional_parent_ids:
                parent_filters = [Categories.deleted_at.is_(None), Categories.id.in_(additional_parent_ids)]
                additional_parents, _ = await categories_repository.get_all_categories(parent_filters, session, 0, 1000)

            all_relevant_parents = matched_parents + additional_parents

            start_idx = skip
            end_idx = skip + limit
            paginated_parents = all_relevant_parents[start_idx:end_idx]

            paginated_parent_ids = {p.id for p in paginated_parents}
            final_children = [child for child in matched_children if child.parent_id in paginated_parent_ids]

            final_categories = list(paginated_parents) + final_children

            return {
                "data": [
                    {
                        "id": str(cat.id),
                        "name": cat.name,
                        "image": cat.image,
                        "parent_id": str(cat.parent_id) if cat.parent_id else None
                    }
                    for cat in final_categories
                ],
                "total": len(final_categories)
            }
        else:
            parent_filters = [Categories.deleted_at.is_(None), Categories.parent_id.is_(None)]
            parent_categories, parent_total = await categories_repository.get_all_categories(parent_filters, session, skip, limit)

            parent_ids = [cat.id for cat in parent_categories]
            if parent_ids:
                child_filters = [Categories.deleted_at.is_(None), Categories.parent_id.in_(parent_ids)]
                child_categories, _ = await categories_repository.get_all_categories(child_filters, session, 0, 1000)
            else:
                child_categories = []

            all_categories = list(parent_categories) + list(child_categories)

            return {
                "data": [
                    {
                        "id": str(cat.id),
                        "name": cat.name,
                        "image": cat.image,
                        "parent_id": str(cat.parent_id) if cat.parent_id else None
                    }
                    for cat in all_categories
                ],
                "total": parent_total
            }

    async def get_detail_category_service(self, id: str, session: AsyncSession):
        condition = and_(Categories.id == id)
        categories = await categories_repository.get_category(condition, session)

        if categories is None:
            CategoriesException.not_found()

        return {
            "id": str(categories.id),
            "name": categories.name,
            "image": categories.image,
            "parent_id": str(categories.parent_id) if categories.parent_id else None
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

        sub_categories_condition = [Categories.parent_id == id, Categories.deleted_at.is_(None)]
        await categories_repository.delete_sub_categories(sub_categories_condition, session)

        await session.commit()
        return {}
