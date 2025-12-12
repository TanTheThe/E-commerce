from src.crud.material.repositories import MaterialRepository
from src.crud.product.repositories import ProductRepository
from src.database.models import Product, Material
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.material import MaterialException
from src.errors.product import ProductException
from src.schemas.material import ProductMaterialAssignmentModel

material_repository = MaterialRepository()
product_repository = ProductRepository()


class AssignMaterialService:
    async def assign_materials_to_product(self, assignment_data: ProductMaterialAssignmentModel, session: AsyncSession):
        condition = [
            Product.id == assignment_data.product_id,
            Product.deleted_at.is_(None),
            Product.status == "active"
        ]
        product = await product_repository.get_product(session=session, where_conditions=condition)
        if not product:
            ProductException.not_found()

        materials_data = [
            {"material_id": m.material_id, "percentage": m.percentage}
            for m in assignment_data.materials
        ]
        material_ids = [m.material_id for m in assignment_data.materials]

        condition_material_ids = [
            Material.id.in_(material_ids),
            Material.deleted_at.is_(None),
            Material.is_active == True
        ]
        existing_materials = await material_repository.get_all_material(session=session, where_conditions=condition_material_ids)

        if len(existing_materials) != len(material_ids):
            MaterialException.some_materials_not_found()

        total_percentage = sum(m.percentage for m in assignment_data.materials)

        result = await material_repository.assign_materials_to_product(assignment_data.product_id,
                                                                       materials_data, session)

        return {
            "product_id": str(assignment_data.product_id),
            "assigned_materials": len(materials_data),
            "total_percentage": round(total_percentage, 2),
            "materials": materials_data
        }
