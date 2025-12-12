from src.crud.categories.utils import generate_slug
from src.crud.size.services import SizeService
from src.database.models import Categories
from src.errors.size import SizeException
from src.schemas.categories import CategoryUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.categories.repositories import CategoriesRepository
from src.errors.categories import CategoriesException

categories_repository = CategoriesRepository()
size_service = SizeService()

class UpdateCategoryService:
    async def update_category(self, id: str, category_update: CategoryUpdateModel, session: AsyncSession):
        update_data = category_update.model_dump(exclude_unset=True)
        if not update_data:
            CategoriesException.no_fields_update()

        condition = [Categories.id == id, Categories.deleted_at.is_(None)]
        category = await categories_repository.get_category(session=session, where_conditions=condition)

        if not category:
            CategoriesException.not_found()

        if 'type_size' in update_data:
            sizes = await size_service.get_all_size(session)
            valid_types = {s["type"] for s in sizes}

            if update_data['type_size'] not in valid_types:
                SizeException.size_not_exists()

        if 'name' in update_data:
            new_slug = generate_slug(update_data['name'])

            existing_category = await categories_repository.get_category(session=session, where_conditions=[Categories.slug == new_slug])
            if existing_category and str(existing_category.id) != id:
                CategoriesException.slug_exists()

            update_data['slug'] = new_slug

        if 'parent_id' in update_data:
            parent_id = update_data['parent_id']
            if parent_id is None:
                pass
            else:
                if str(parent_id) == id:
                    CategoriesException.invalid_parent()

                parent = await categories_repository.get_category(session=session,
                                                                  where_conditions=[Categories.id == parent_id,
                                                                                    Categories.deleted_at.is_(None)])
                if not parent:
                    CategoriesException.parent_not_found()

                await self.check_circular_reference(id, parent_id, session)

                is_descendant = await self.is_descendant(parent_id, id, session)
                if is_descendant:
                    CategoriesException.cant_set_child_to_parent()

        await categories_repository.update_categories(category, update_data, session)
        await session.commit()
        await session.refresh(category)

        response_dict = {
            "id": str(category.id),
            "name": category.name,
            "slug": category.slug,
            "image": category.image,
            "parent_id": str(category.parent_id) if category.parent_id else None,
            "type_size": category.type_size
        }

        return response_dict

    async def check_circular_reference(self, category_id: str, new_parent_id: str, session: AsyncSession, max_depth: int = 10):
        current_parent_id = new_parent_id
        depth = 0

        while current_parent_id and depth < max_depth:
            if str(current_parent_id) == category_id:
                CategoriesException.error_loop_category()

            parent = await categories_repository.get_category(
                session=session,
                where_conditions=[Categories.id == current_parent_id, Categories.deleted_at.is_(None)]
            )

            if not parent or not parent.parent_id:
                break

            current_parent_id = parent.parent_id
            depth += 1

        if depth >= max_depth:
            CategoriesException.category_tree_so_deep()


    async def is_descendant(self, potential_parent_id: str, category_id: str, session: AsyncSession):
        children_list, _ = await categories_repository.get_all_categories(
            session=session,
            where_conditions=[
                Categories.parent_id == category_id,
                Categories.deleted_at.is_(None)
            ],
            skip=0,
            limit=1000
        )

        for child in children_list:
            if child.id == potential_parent_id:
                return True

            if await self.is_descendant(potential_parent_id, child.id, session):
                return True

        return False

