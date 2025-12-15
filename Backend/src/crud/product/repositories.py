from typing import Optional, List, Any, Dict, Tuple
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
        product_data_dict = product_data.model_dump(
        exclude={"categories_id", "product_variant", "materials", "tags_id"}
        )
        new_product = Product(**product_data_dict)
        new_product.status = "active"
        new_product.created_at = datetime.now()

        session.add(new_product)
        await session.flush()

        return new_product


    async def get_all_product(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):
        if select_columns is None:
            query = select(Product)
        else:
            query = select(*select_columns).select_from(Product)

        if joins:
            for table, config in joins:
                if config.get('type') == 'outer':
                    query = query.outerjoin(table, config['on'])
                else:
                    query = query.join(table, config['on'])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.exec(count_query)
        total = count_result.one() or 0

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        products = result.unique().all()

        return products, total


    async def get_product(self, session: AsyncSession,
                        select_columns: Optional[List[Any]] = None,
                        joins: Optional[List[Tuple[Any, dict]]] = None,
                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                        group_by_columns: Optional[List[Any]] = None,
                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                        order_by: Optional[Any] = None,
                        options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(Product)
        else:
            query = select(*select_columns).select_from(Product)

        if joins:
            for table, config in joins:
                if config.get("type") == "outer":
                    query = query.outerjoin(table, config["on"])
                else:
                    query = query.join(table, config["on"])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)

        product = result.one_or_none()

        return product


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


    async def delete_product(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        product_to_delete = await self.get_product(condition, session)

        if product_to_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Không tìm thấy sản phẩm.",
                    "error_code": "product_006",
                },
            )
        product_to_delete.deleted_at = datetime.now()

        return {"deleted_id": str(product_to_delete.id)}

    async def delete_multiple_product(self, data: DeleteMultipleProductModel, session: AsyncSession):
        conditions = [Product.id.in_(data.product_ids), Product.deleted_at.is_(None)]
        products = await self.get_all_product(conditions, session, None, 0, 1000)
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
                Product.avg_rating.label("avg_rating"),
                Product.total_sold.label("total_sold")
            )
            .join(Categories_Product, Categories_Product.product_id == Product.id)
            .join(Categories, Categories_Product.categories_id == Categories.id)
            .outerjoin(Product_Variant, Product_Variant.product_id == Product.id)
            .outerjoin(Special_Offer, Special_Offer.id == Product.special_offer_id)
            .where(conditions)
            .group_by(Product.id, Product.name, Product.images, Product.popularity_score, Special_Offer.discount, Special_Offer.type, Product.avg_rating, Product.total_sold)
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
                Product.avg_rating.label("avg_rating"),
                Product.total_sold.label("total_sold")
            )
            .join(Categories_Product, Categories_Product.product_id == Product.id)
            .join(Categories, Categories_Product.categories_id == Categories.id)
            .outerjoin(Product_Variant, Product_Variant.product_id == Product.id)
            .outerjoin(Special_Offer, Special_Offer.id == Product.special_offer_id)
            .where(Special_Offer.discount.isnot(None), Special_Offer.type == "percent")
            .group_by(Product.id, Product.name, Product.images, Special_Offer.discount, Product.avg_rating, Product.total_sold)
            .order_by(desc(Special_Offer.discount))
            .limit(limit)
        )

        result = await session.exec(stmt)
        return result.all()