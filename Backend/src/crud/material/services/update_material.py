from src.crud.material.repositories import MaterialRepository
from src.crud.material.utils import generate_slug
from src.crud.product.repositories import ProductRepository
from src.database.models import Material
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.material import MaterialException
from src.schemas.material import MaterialUpdateModel

material_repository = MaterialRepository()
product_repository = ProductRepository()


class UpdateMaterialService:
    async def update_material(self, material_id: str, material_data: MaterialUpdateModel,
                                      session: AsyncSession):
        condition = [Material.id == material_id, Material.deleted_at.is_(None)]
        existing_material = await material_repository.get_material(session=session, where_conditions=condition)

        if not existing_material:
            MaterialException.material_not_found()

        new_slug = None
        if material_data.name and material_data.name != existing_material.name:
            condition_check_name = [
                Material.name == material_data.name,
                Material.deleted_at.is_(None),
                Material.id != material_id
            ]
            duplicate_material = await material_repository.get_material(session=session, where_conditions=condition_check_name)
            if duplicate_material:
                MaterialException.material_name_exists()

            new_slug = await self.generate_unique_slug(material_data.name, material_id, session)

        condition = and_(Material.id == material_id)
        updated_material_tuple = await material_repository.update_material(condition, material_data, new_slug, session)

        updated_material = updated_material_tuple[0]

        return {
            "id": str(updated_material.id),
            "name": updated_material.name,
            "slug": updated_material.slug,
            "is_active": updated_material.is_active,
            "updated_at": str(updated_material.updated_at) if updated_material.updated_at else None
        }

    async def generate_unique_slug(self, name: str, exclude_id: str, session: AsyncSession) -> str:
        base_slug = generate_slug(name)
        slug = base_slug
        counter = 1

        while True:
            condition = [
                Material.slug == slug,
                Material.deleted_at.is_(None),
                Material.id != exclude_id
            ]
            existing = await material_repository.get_material(session=session, where_conditions=condition)
            if not existing:
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

