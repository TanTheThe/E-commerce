from typing import Optional, List, Any, Dict
from sqlalchemy import ColumnElement
from src.database.models import Product, Product_Variant, Categories, Evaluate, Order_Detail, Order, Categories_Product, \
    Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, update, func, and_, desc
from sqlalchemy import select, func, and_, desc, case
from sqlalchemy.orm import aliased
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import noload, selectinload
from uuid import UUID

from src.errors.product import ProductException
from src.schemas.product import DeleteMultipleProductModel


class ProductRepository:
    async def create_product(self, product_data, session: AsyncSession):
        product_data_dict = product_data.model_dump(exclude={"categories_id", "product_variant"})

        new_product = Product(
            **product_data_dict
        )

        new_product.status = "active"
        new_product.created_at = datetime.now()

        session.add(new_product)
        await session.flush()

        if product_data.product_variant:
            skus = [variant.sku for variant in product_data.product_variant if variant.sku]
            if skus:
                stmt = select(Product_Variant.sku).where(
                    Product_Variant.sku.in_(skus),
                    Product_Variant.deleted_at.is_(None)
                )
                existing_skus_result = await session.exec(stmt)
                existing_skus = set(existing_skus_result.all())

                if existing_skus:
                    ProductException.sku_exists(existing_skus)

        return new_product

    async def get_all_product(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession,
                              joins: list = None, skip: int = 0, limit: int = 10, order_by_clause=None):
        count_stmt = select(func.count(Product.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Product).options(
            *joins if joins else []
        ).where(*conditions).offset(skip).limit(limit)

        if order_by_clause is not None:
            statement = statement.order_by(order_by_clause)

        result = await session.exec(statement)
        products = result.unique().all()

        return products, total


    async def get_product(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Product).options(
            *joins if joins else []
        ).where(conditions)

        result = await session.exec(statement)

        return result.one_or_none()

    async def update_product(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()
        await session.commit()

        return data_need_update


    async def update_product_some_field(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Product)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)
        await session.commit()


    async def delete_product(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        joins = [
            noload(Product.order_detail),
            noload(Product.categories),
            noload(Product.evaluate),
            noload(Product.special_offer),
            noload(Product.categories_product),
            noload(Product.product_variant),
        ]
        product_to_delete = await self.get_product(condition, session, joins)

        if product_to_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Không tìm thấy sản phẩm.",
                    "error_code": "product_006",
                },
            )
        product_to_delete.deleted_at = datetime.now()
        await session.commit()

        return {"deleted_id": str(product_to_delete.id)}

    async def delete_multiple_product(self, data: DeleteMultipleProductModel, session: AsyncSession):
        conditions = [Product.id.in_(data.product_ids), Product.deleted_at.is_(None)]
        joins = [
            noload(Product.order_detail),
            noload(Product.categories),
            noload(Product.evaluate),
            noload(Product.special_offer),
            noload(Product.categories_product),
            noload(Product.product_variant)
        ]
        products = await self.get_all_product(conditions, session, joins, 0, 1000)
        existing_ids = {str(row.id) for row in products}
        missing_ids = set(data.product_ids) - existing_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không tìm thấy các mã sản phẩm: {list(missing_ids)}"
            )
        stmt = update(Product).where(Product.id.in_(data.product_ids)).values(deleted_at=datetime.now())
        await session.exec(stmt)
        await session.commit()

        return data.product_ids

    async def count_products(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        base_condition = Product.deleted_at.is_(None)

        if conditions is not None:
            base_condition = and_(base_condition, conditions)

        statement = (
            select(func.count())
            .select_from(Product)
            .where(base_condition)
        )

        result = await session.exec(statement)
        return result.one_or_none() or 0

    async def get_popular_products_by_category(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, limit_per_category: int = 12):
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.images.label("images"),
                func.min(Product_Variant.price).label("min_price"),
                func.array_agg(
                    func.distinct(
                        func.jsonb_build_object(
                            "id", Categories.id,
                            "name", Categories.name
                        )
                    )
                ).label("categories"),
                Special_Offer.discount.label("discount"),
                Special_Offer.type.label("type_offer"),
                Product.avg_rating.label("avg_rating")
            )
            .join(Categories_Product, Categories_Product.product_id == Product.id)
            .join(Categories, Categories_Product.categories_id == Categories.id)
            .outerjoin(Product_Variant, Product_Variant.product_id == Product.id)
            .outerjoin(Special_Offer, Special_Offer.id == Product.special_offer_id)
            .where(conditions)
            .group_by(Product.id, Product.name, Product.images, Product.popularity_score, Special_Offer.discount, Special_Offer.type, Product.avg_rating)
            .order_by(desc(Product.popularity_score))
            .limit(limit_per_category)
        )

        result = await session.exec(stmt)
        return result.all()


    async def get_top_discount(self, session: AsyncSession, limit: int = 12):
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.images.label("images"),
                func.min(Product_Variant.price).label("min_price"),
                func.array_agg(
                    func.distinct(
                        func.jsonb_build_object(
                            "id", Categories.id,
                            "name", Categories.name
                        )
                    )
                ).label("categories"),
                Special_Offer.discount.label("discount"),
                Product.avg_rating.label("avg_rating")
            )
            .join(Categories_Product, Categories_Product.product_id == Product.id)
            .join(Categories, Categories_Product.categories_id == Categories.id)
            .outerjoin(Product_Variant, Product_Variant.product_id == Product.id)
            .outerjoin(Special_Offer, Special_Offer.id == Product.special_offer_id)
            .where(Special_Offer.discount.isnot(None), Special_Offer.type == "percent")
            .group_by(Product.id, Product.name, Product.images, Special_Offer.discount, Product.avg_rating)
            .order_by(desc(Special_Offer.discount))
            .limit(limit)
        )

        result = await session.exec(stmt)
        return result.all()