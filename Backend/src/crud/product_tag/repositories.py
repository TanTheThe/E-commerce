from datetime import datetime

from sqlalchemy import delete
from sqlmodel import and_

from src.database.models import Product_Material, Product_Tag
from sqlmodel.ext.asyncio.session import AsyncSession


class ProductTagRepository:
    async def create_product_tag(self, tag_ids, product_id, session: AsyncSession):
        for tag_id in tag_ids:
            product_tag = Product_Tag(
                product_id=product_id,
                tag_id=tag_id,
                created_at=datetime.now(),
            )
            session.add(product_tag)

    async def delete_product_tag(self, product_id: str, session: AsyncSession):
        delete_stmt = delete(Product_Tag).where(and_(Product_Tag.product_id == product_id))
        await session.exec(delete_stmt)









