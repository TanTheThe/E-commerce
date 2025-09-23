from src.crud.material.repositories import MaterialRepository
from src.crud.material.utils import generate_slug
from src.crud.product.repositories import ProductRepository
from src.database.models import Product, Material
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, asc, desc
from src.errors.material import MaterialException
from src.errors.product import ProductException
from typing import Optional

from src.schemas.material import MaterialCreateModel, ProductMaterialAssignmentModel, MaterialUpdateModel, \
    DeleteMultipleMaterialsModel

material_repository = MaterialRepository()
product_repository = ProductRepository()


class MaterialService:
    async def create_material_service(self, material_data: MaterialCreateModel, session: AsyncSession):
        condition = and_(Material.name == material_data.name, Material.deleted_at.is_(None))
        existing_material = await material_repository.get_material(condition, session)

        if existing_material:
            MaterialException.material_name_exists()

        slug = generate_slug(material_data.name)
        slug = await self._generate_unique_slug(slug, session)

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

    async def _generate_unique_slug(self, base_slug: str, session: AsyncSession, force_new: bool = False) -> str:
        if not force_new:
            condition_slug = and_(Material.slug == base_slug, Material.deleted_at.is_(None))
            existing_slug = await material_repository.get_material(condition_slug, session)
            if not existing_slug:
                return base_slug

        counter = 1
        while True:
            new_slug = f"{base_slug}-{counter}"
            condition_slug = and_(Material.slug == new_slug, Material.deleted_at.is_(None))
            existing_slug = await material_repository.get_material(condition_slug, session)
            if not existing_slug:
                return new_slug
            counter += 1

    async def get_all_materials_admin(self, search: Optional[str], is_active: Optional[bool],
                                      sort_by: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = [Material.deleted_at.is_(None)]

        if search:
            conditions.append(Material.name.ilike(f"%{search}%"))

        if is_active is not None:
            conditions.append(Material.is_active == is_active)

        order_by_clause = None

        if sort_by == "name_asc":
            order_by_clause = asc(Material.name)
        elif sort_by == "name_desc":
            order_by_clause = desc(Material.name)
        elif sort_by == "created_asc":
            order_by_clause = asc(Material.created_at)
        else:
            order_by_clause = desc(Material.created_at)

        materials, total = await material_repository.get_all_material(conditions, session, skip, limit,
                                                                      order_by_clause=order_by_clause)

        materials_list = []
        for material in materials:
            material_dict = {
                "id": str(material.id),
                "name": material.name,
                "slug": material.slug,
                "is_active": material.is_active,
                "product_count": material.products_count,
                "created_at": str(material.created_at) if material.created_at else None
            }
            materials_list.append(material_dict)

        return {
            "data": materials_list,
            "total": total
        }

    async def get_all_materials_customer(self, search: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = [Material.deleted_at.is_(None)]

        if search:
            conditions.append(Material.name.ilike(f"%{search}%"))

        materials, total = await material_repository.get_all_material(conditions, session, skip, limit)

        materials_list = []
        for material in materials:
            material_dict = {
                "id": str(material.id),
                "name": material.name,
                "slug": material.slug,
                "is_active": material.is_active,
                "product_count": material.products_count,
            }
            materials_list.append(material_dict)

        return {
            "data": materials_list,
            "total": total
        }

    async def assign_materials_to_product(self, assignment_data: ProductMaterialAssignmentModel, session: AsyncSession):
        condition = and_(Product.id == assignment_data.product_id, Product.deleted_at.is_(None),
                         Product.status == "active")
        product = await product_repository.get_product(condition, session)
        if not product:
            ProductException.not_found()

        material_ids = [m["material_id"] for m in assignment_data.materials]
        condition_material_ids = [Material.id.in_(material_ids), Material.deleted_at.is_(None)]
        existing_materials = await material_repository.get_all_material(condition_material_ids, session)

        if len(existing_materials) != len(material_ids):
            MaterialException.some_materials_not_found()

        total_percentage = sum([m.get("percentage", 0) for m in assignment_data.materials])
        if total_percentage > 100:
            MaterialException.percentage_exceeds_100()

        result = await material_repository.assign_materials_to_product(assignment_data.product_id,
                                                                       assignment_data.materials, session)

        return {
            "product_id": str(assignment_data.product_id),
            "assigned_materials": len(assignment_data.materials),
            "total_percentage": total_percentage
        }

    async def update_material_service(self, material_id: str, material_data: MaterialUpdateModel,
                                      session: AsyncSession):
        condition = and_(Material.id == material_id, Material.deleted_at.is_(None))
        existing_material = await material_repository.get_material(condition, session)

        if not existing_material:
            MaterialException.material_not_found()

        if material_data.name and material_data.name != existing_material.name:
            condition_check_name = and_(Material.name == material_data.name, Material.deleted_at.is_(None))
            duplicate_material = await material_repository.get_material(condition_check_name, session)

            if duplicate_material:
                MaterialException.material_name_exists()

        new_slug = None
        if material_data.name and material_data.name != existing_material.name:
            new_slug = generate_slug(material_data.name)
            condition_slug_1 = and_(Material.slug == new_slug, Material.deleted_at.is_(None))
            existing_slug = await material_repository.get_material(condition_slug_1, session)
            if existing_slug and str(existing_slug.id) != material_id:
                counter = 1
                temp_slug = ""
                while existing_slug:
                    temp_slug = f"{new_slug}-{counter}"
                    condition_slug_2 = and_(Material.slug == temp_slug, Material.deleted_at.is_(None))
                    existing_slug = await material_repository.get_material(condition_slug_2, session)
                    if not existing_slug or str(existing_slug.id) == material_id:
                        break
                    counter += 1
                new_slug = temp_slug

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

    async def delete_material(self, material_id: str, session: AsyncSession):
        condition = and_(Material.id == material_id, Material.deleted_at.is_(None))
        return await material_repository.delete_material(condition, session)

    async def delete_multiple_materials(self, data: DeleteMultipleMaterialsModel, session: AsyncSession):
        material_ids = await material_repository.delete_multiple_materials(data, session)
        return material_ids