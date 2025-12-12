from src.crud.material.repositories import MaterialRepository
from src.crud.product.repositories import ProductRepository
from src.database.models import Material
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import asc, desc
from typing import Optional

material_repository = MaterialRepository()
product_repository = ProductRepository()


class GetAllMaterialsService:
    async def get_all_materials_admin(self, search: Optional[str], is_active: Optional[bool],
                                      sort_by: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = [Material.deleted_at.is_(None)]

        if search:
            search_clean = search.strip().replace('%', '\\%').replace('_', '\\_')
            conditions.append(Material.name.ilike(f"%{search_clean}%"))

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

        materials, total = await material_repository.get_all_material(session=session, where_conditions=conditions,
                                                                      skip=skip, limit=limit, order_by=order_by_clause)

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
        conditions = [Material.deleted_at.is_(None), Material.is_active == True]

        if search:
            search_clean = search.strip().replace('%', '\\%').replace('_', '\\_')
            conditions.append(Material.name.ilike(f"%{search_clean}%"))

        materials, total = await material_repository.get_all_material(session=session, where_conditions=conditions,
                                                                      skip=skip, limit=limit)

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