from datetime import datetime

from sqlalchemy import delete
from sqlmodel import and_

from src.database.models import Product_Material
from sqlmodel.ext.asyncio.session import AsyncSession


class ProductMaterialRepository:
    async def create_product_material(self, materials_data, product_id, session: AsyncSession):
        if not materials_data:
            return
        
        new_objects = [
            Product_Material(
                product_id=product_id,
                material_id=material_data.material_id,
                percentage=material_data.percentage,
                created_at=datetime.now(),
            )
            for material_data in materials_data
        ]
        
        session.add_all(new_objects)
        await session.flush()


    async def delete_product_material(self, product_id: str, session: AsyncSession):
        delete_stmt = delete(Product_Material).where(and_(Product_Material.product_id == product_id))
        await session.exec(delete_stmt)









