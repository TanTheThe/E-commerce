from typing import Optional
from sqlalchemy import ColumnElement
from src.database.models import Product_Variant
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, update
from datetime import datetime
from fastapi import HTTPException, status
from src.schemas.product_variant import ProductVariantCreateModel
from src.errors.product import ProductException


class ProductVariantRepository:
    async def create_product_variant(self, product_variant_data, product_id, session: AsyncSession):
        if product_variant_data and isinstance(product_variant_data[0] if product_variant_data else None, dict):
            product_variant_data = [ProductVariantCreateModel(**item) for item in product_variant_data]

        new_objects = [
            Product_Variant(
                product_id=product_id,
                size=item.size,
                color=item.color,
                price=item.price,
                quantity=item.quantity,
                sku=item.sku,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            for item in product_variant_data
        ]

        session.add_all(new_objects)


    async def get_all_product_variant(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Product_Variant).order_by(desc(Product_Variant.created_at))
        if conditions is not None:
            statement = statement.where(conditions)
        if joins is not None:
            statement = statement.options(*joins)

        result = await session.exec(statement)
        return result.all()


    async def get_product_variant(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(Product_Variant).where(conditions)
        result = await session.exec(statement)

        return result.one_or_none()


    async def update_product_variant(self, update_data:dict, condition: ColumnElement[bool], session: AsyncSession):
        statement = (
            update(Product_Variant)
            .where(condition)
            .values(
                **update_data
            )
        )

        await session.exec(statement)


    async def delete_product_variant(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        product_variant_delete = await self.get_product_variant(condition, session)

        if product_variant_delete is None:
            ProductException.not_found_variant_to_delete()

        product_variant_delete.deleted_at = datetime.now()

        return {}








