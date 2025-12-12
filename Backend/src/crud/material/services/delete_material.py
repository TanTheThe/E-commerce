from src.crud.material.repositories import MaterialRepository
from src.crud.product.repositories import ProductRepository
from src.database.models import Material
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.material import DeleteMultipleMaterialsModel

material_repository = MaterialRepository()
product_repository = ProductRepository()


class DeleteMaterialService:
    async def delete_material(self, material_id: str, session: AsyncSession):
        condition = [Material.id == material_id, Material.deleted_at.is_(None)]
        return await material_repository.delete_material(condition, session)

    async def delete_multiple_materials(self, data: DeleteMultipleMaterialsModel, session: AsyncSession):
        material_ids = await material_repository.delete_multiple_materials(data, session)
        return material_ids