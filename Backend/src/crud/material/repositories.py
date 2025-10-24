from typing import Optional, List, Dict
from sqlalchemy import ColumnElement, delete
from src.database.models import Product, Material, Product_Material
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, update
from datetime import datetime
from src.errors.material import MaterialException
from src.schemas.material import MaterialUpdateModel, DeleteMultipleMaterialsModel


class MaterialRepository:
    async def create_material(self, material_data_dict, session: AsyncSession):
        new_material = Material(
            **material_data_dict,
            created_at=datetime.now()
        )
        session.add(new_material)
        await session.flush()

        return new_material


    async def get_all_material(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, skip: int = 0, limit: int = 10,
                               joins: list = None, order_by_clause=None):
        count_stmt = select(func.count(Material.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Material).where(*conditions).options(
            *joins if joins else []
        ).offset(skip).limit(limit)
        
        if order_by_clause is not None:
            statement = statement.order_by(order_by_clause)

        result = await session.exec(statement)

        materials = result.all()

        return materials, total


    async def get_material(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Material).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.one_or_none()


    async def update_material(self, condition: Optional[ColumnElement[bool]], material_data: MaterialUpdateModel,
                              new_slug: Optional[str], session: AsyncSession):
        update_data = {}

        if material_data.name is not None:
            update_data['name'] = material_data.name
        if new_slug:
            update_data['slug'] = new_slug
        if material_data.is_active is not None:
            update_data['is_active'] = material_data.is_active

        update_data['updated_at'] = datetime.now()

        stmt = (
            update(Material)
            .where(condition)
            .values(**update_data)
            .returning(Material)
        )
        result = await session.exec(stmt)
        await session.commit()

        return result.one_or_none()


    async def count_products_by_material(self, material_id: str, session: AsyncSession):
        query = select(func.count(Product_Material.product_id)).where(
            Product_Material.material_id == material_id
        ).join(
            Product, and_(Product_Material.product_id == Product.id)
        ).where(
            Product.deleted_at.is_(None), Product.status == "active"
        )
        result = await session.exec(query)
        return result.one_or_none()


    async def assign_materials_to_product(self, product_id: str, materials: List[Dict], session: AsyncSession):
        delete_stmt = delete(Product_Material).where(and_(Product_Material.product_id == product_id))
        await session.exec(delete_stmt)

        for material_data in materials:
            product_material = Product_Material(
                product_id=product_id,
                material_id=material_data["material_id"],
                percentage=material_data.get("percentage"),
                created_at=datetime.now()
            )
            session.add(product_material)

        await session.commit()
        return True


    async def delete_material(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        material_delete = await self.get_material(condition, session)

        if material_delete is None:
            MaterialException.material_not_found()

        material_delete.deleted_at = datetime.now()
        await session.commit()

        return str(material_delete.id)
    
    async def delete_multiple_materials(self, data: DeleteMultipleMaterialsModel, session: AsyncSession):
        conditions = [Material.id.in_(data.material_ids), Material.deleted_at.is_(None)]
        materials, _ = await self.get_all_material(conditions, session)
        existing_ids = {str(row.id) for row in materials}
        missing_ids = set(data.material_ids) - existing_ids
        if missing_ids:
            MaterialException.some_materials_not_found()

        condition_delete = and_(Material.id.in_(data.material_ids), Material.deleted_at.is_(None))
        stmt = update(Material).where(condition_delete).values(deleted_at=datetime.now())

        await session.exec(stmt)
        await session.commit()

        return data.material_ids
