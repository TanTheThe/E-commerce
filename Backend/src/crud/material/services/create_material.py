from src.crud.material.repositories import MaterialRepository
from src.crud.material.utils import generate_slug
from src.crud.product.repositories import ProductRepository
from src.database.models import Material
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.material import MaterialException
from src.schemas.material import MaterialCreateModel

material_repository = MaterialRepository()
product_repository = ProductRepository()


class CreateMaterialService:
    async def create_material(self, material_data: MaterialCreateModel, session: AsyncSession):
        condition = [Material.name == material_data.name, Material.deleted_at.is_(None)]
        existing_material = await material_repository.get_material(session=session, where_conditions=condition)

        if existing_material:
            MaterialException.material_name_exists()

        slug = generate_slug(material_data.name)
        slug = await self.generate_unique_slug(slug, session)

        new_material_dict = {
            "name": material_data.name,
            "slug": slug,
            "is_active": material_data.is_active
        }

        material = await material_repository.create_material(new_material_dict, session)

        await session.commit()
        await session.refresh(material)

        return {
            "id": str(material.id),
            "name": material.name,
            "slug": material.slug,
            "is_active": material.is_active,
            "created_at": str(material.created_at) if material.created_at else None
        }

    async def generate_unique_slug(self, base_slug: str, session: AsyncSession, force_new: bool = False) -> str:
        if not force_new:
            condition_slug = [Material.slug == base_slug, Material.deleted_at.is_(None)]
            existing_slug = await material_repository.get_material(session=session, where_conditions=condition_slug)
            if not existing_slug:
                return base_slug

        counter = 1
        while True:
            new_slug = f"{base_slug}-{counter}"
            condition_slug = [Material.slug == new_slug, Material.deleted_at.is_(None)]
            existing_slug = await material_repository.get_material(session=session, where_conditions=condition_slug)
            if not existing_slug:
                return new_slug
            counter += 1