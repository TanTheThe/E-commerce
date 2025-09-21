from typing import Optional, List, Dict, Any
from sqlalchemy import ColumnElement
from sqlalchemy.orm import noload, load_only

from src.database.models import Brand, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, update
from datetime import datetime
from src.errors.brand import BrandException
from src.errors.color import ColorException
from src.schemas.brand import DeleteMultipleBrandsModel


class BrandRepository:
    async def create_brand(self, brand_data_dict, session: AsyncSession):
        new_brand = Brand(
            **brand_data_dict,
            created_at=datetime.now()
        )
        session.add(new_brand)

        return new_brand


    async def get_all_brand(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, skip: int = 0, limit: int = 10
                            , joins: list = None, order_by_clause=None):
        count_stmt = select(func.count(Brand.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Brand).where(*conditions).options(
            *joins if joins else []
        ).offset(skip).limit(limit)
        
        if order_by_clause is not None:
            statement = statement.order_by(order_by_clause)

        result = await session.exec(statement)

        colors = result.all()

        return colors, total


    async def get_brand(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Brand).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.one_or_none()


    async def update_brand(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any],
                                        session: AsyncSession):
        stmt = (
            update(Brand)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)
        
        
    async def count_products_by_brand(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        query = select(func.count(Product.id)).where(condition)
        result = await session.exec(query)
        return result.one_or_none()


    async def delete_brand(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        brand_delete = await self.get_brand(condition, session)

        if brand_delete is None:
            BrandException.brand_not_found()

        brand_delete.deleted_at = datetime.now()
        await session.commit()

        return str(brand_delete.id)
    
    async def delete_multiple_brand(self, data: DeleteMultipleBrandsModel, session: AsyncSession):
        conditions = [Brand.id.in_(data.brand_ids), Brand.deleted_at.is_(None)]
        brands = await self.get_all_brand(conditions, session)
        existing_ids = {str(row.id) for row in brands}
        missing_ids = set(data.brand_ids) - existing_ids
        if missing_ids:
            BrandException.brand_not_found()
            
        stmt = update(Brand).where(Brand.id.in_(data.brand_ids)).values(deleted_at=datetime.now())
        await session.exec(stmt)
        await session.commit()

        return data.brand_ids
