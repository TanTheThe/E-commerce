from src.crud.categories.utils import generate_slug
from src.crud.size.services import SizeService
from src.database.models import Categories
from src.errors.size import SizeException
from src.schemas.categories import CategoriesCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.categories.repositories import CategoriesRepository
from src.errors.categories import CategoriesException

categories_repository = CategoriesRepository()
size_service = SizeService()

class CreateCategoryService:
    async def create_category(self, categories_data: CategoriesCreateModel, session: AsyncSession):
        sizes = await size_service.get_all_size(session)
        valid_types = {s["type"] for s in sizes}

        if categories_data.type_size not in valid_types:
            SizeException.size_not_exists()

        slug = generate_slug(categories_data.name)

        condition_check_exist = [Categories.slug == slug]
        existing_category = await categories_repository.get_category(session=session, where_conditions=condition_check_exist)

        if existing_category:
            CategoriesException.slug_exists()

        if categories_data.parent_id:
            condition_check_parent = [Categories.parent_id == categories_data.parent_id]
            parent_category = await categories_repository.get_category(session=session, where_conditions=condition_check_parent)

            if not parent_category:
                CategoriesException.parent_not_found()

        categories_data_with_slug = categories_data.model_dump()
        categories_data_with_slug['slug'] = slug

        new_categories = await categories_repository.create_categories(categories_data_with_slug, session)

        new_categories_dict = {
            "id": str(new_categories.id),
            "name": new_categories.name,
            "slug": new_categories.slug,
            "image": new_categories.image,
            "parent_id": str(new_categories.parent_id) if new_categories.parent_id else None,
            "type_size": new_categories.type_size
        }

        return new_categories_dict
