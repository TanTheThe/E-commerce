from datetime import datetime

from sqlalchemy import delete
from sqlmodel import and_

from src.database.models import Product_Material, Product_Tag
from sqlmodel.ext.asyncio.session import AsyncSession


class ProductTagRepository:
    async def create_product_tag(self, tag_ids, product_id, session: AsyncSession):
        if not tag_ids:
            return
    
        new_objects = [
            Product_Tag(
                product_id=product_id,
                tag_id=tag_id,
                created_at=datetime.now(),
            )
            for tag_id in tag_ids
        ]
        
        session.add_all(new_objects)
        await session.flush()

    async def delete_product_tag(self, product_id: str, session: AsyncSession):
        delete_stmt = delete(Product_Tag).where(and_(Product_Tag.product_id == product_id))
        await session.exec(delete_stmt)









