from src.crud.size.services import SizeService
from src.database.models import Categories
from src.schemas.categories import CategoriesFilterModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.categories.repositories import CategoriesRepository
from src.errors.categories import CategoriesException

categories_repository = CategoriesRepository()
size_service = SizeService()

class GetAllCategoriesService:
    async def get_all_categories(self, filter_data: CategoriesFilterModel, session: AsyncSession,
                                         skip: int = 0, limit: int = 5):
        if skip < 0:
            CategoriesException.skip_cant_be_negative()

        if limit < 1 or limit > 100:
            CategoriesException.limit_must_be_1_to_100()

        sizes = await size_service.get_all_size(session)
        size_map = {s["type"]: {"id": str(s["id"]), "name": s["name"], "type": s["type"]} for s in sizes}

        if filter_data.type_size and filter_data.type_size not in size_map:
            CategoriesException.type_size_not_exist()

        if filter_data.parent_id:
            parent_exists = await categories_repository.get_category(session=session, where_conditions=[Categories.parent_id == filter_data.parent_id])
            if not parent_exists:
                CategoriesException.parent_not_found()

        if filter_data.search:
            filters = [Categories.deleted_at.is_(None), Categories.name.ilike(f"%{filter_data.search}%")]
            if filter_data.type_size:
                filters.append(Categories.type_size == filter_data.type_size)
            if filter_data.parent_id:
                filters.append(Categories.parent_id == filter_data.parent_id)

            matched_categories, _ = await categories_repository.get_all_categories(session=session, where_conditions=filters, skip=0, limit=1000)

            matched_parents = [cat for cat in matched_categories if cat.parent_id is None]
            matched_children = [cat for cat in matched_categories if cat.parent_id is not None]

            additional_parent_ids = {cat.parent_id for cat in matched_children if cat.parent_id} - {p.id for p in matched_parents}
            additional_parents = []
            if additional_parent_ids:
                parent_filters = [Categories.deleted_at.is_(None), Categories.id.in_(additional_parent_ids)]

                additional_parents, _ = await categories_repository.get_all_categories(session=session, where_conditions=parent_filters, skip=0, limit=1000)

            all_relevant_parents = matched_parents + additional_parents

            start_idx = skip
            end_idx = skip + limit
            paginated_parents = all_relevant_parents[start_idx:end_idx]

            paginated_parent_ids = {p.id for p in paginated_parents}
            final_children = [child for child in matched_children if child.parent_id in paginated_parent_ids]

            final_categories = list(paginated_parents) + final_children
            total = len(all_relevant_parents)

        else:
            filters = [Categories.deleted_at.is_(None), Categories.parent_id.is_(None)]
            if filter_data.type_size:
                filters.append(Categories.type_size == filter_data.type_size)
            if filter_data.parent_id:
                filters = [
                    Categories.deleted_at.is_(None),
                    Categories.parent_id == filter_data.parent_id
                ]
                if filter_data.type_size:
                    filters.append(Categories.type_size == filter_data.type_size)

            parent_categories, total = await categories_repository.get_all_categories(session=session, where_conditions=filters, skip=skip, limit=limit)

            parent_ids = [cat.id for cat in parent_categories]
            if parent_ids and not filter_data.parent_id:
                child_filters = [
                    Categories.deleted_at.is_(None),
                    Categories.parent_id.in_(parent_ids)
                ]
                child_categories, _ = await categories_repository.get_all_categories(session=session, where_conditions=child_filters, skip=0, limit=1000)
            else:
                child_categories = []

            final_categories = list(parent_categories) + list(child_categories)

        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "data": [
                {
                    "id": str(cat.id),
                    "name": cat.name,
                    "image": cat.image,
                    "slug": cat.slug,
                    "parent_id": str(cat.parent_id) if cat.parent_id else None,
                    "type_size": cat.type_size,
                }
                for cat in final_categories
            ],
            "total": total,
            "page": current_page,
            "limit": limit,
            "total_pages": total_pages,
            "sizes": list(size_map.values())
        }
