from typing import Optional
from sqlalchemy import ColumnElement
from sqlalchemy.orm import noload

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

        new_objects = []
        for item in product_variant_data:
            if item.color_id:
                new_variant = Product_Variant(
                    product_id=product_id,
                    size=item.size,
                    color_id=item.color_id,
                    price=item.price,
                    quantity=item.quantity,
                    sku=item.sku,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                new_objects.append(new_variant)

            elif item.color_name and item.color_code:
                new_variant = Product_Variant(
                    product_id=product_id,
                    size=item.size,
                    color_name=item.color_name,
                    color_code=item.color_code,
                    price=item.price,
                    quantity=item.quantity,
                    sku=item.sku,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                new_objects.append(new_variant)

        session.add_all(new_objects)


    async def get_all_product_variant(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Product_Variant).options(
            noload(Product_Variant.order_detail),
            noload(Product_Variant.product),
            noload(Product_Variant.evaluate),
            noload(Product_Variant.color),
            *joins if joins else []
        )

        if conditions is not None:
            statement = statement.where(conditions)

        result = await session.exec(statement)
        return result.all()


    async def get_product_variant(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(Product_Variant).options(
            noload(Product_Variant.order_detail),
            noload(Product_Variant.product),
            noload(Product_Variant.evaluate),
            noload(Product_Variant.color),
        ).where(conditions)
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








