from typing import Optional, Any, List, Tuple
from sqlalchemy import ColumnElement, func, Integer
import uuid
from src.database.models import Product_Variant, Stock, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, update, and_, case
from datetime import datetime
from src.schemas.product_variant import ProductVariantCreateModel
from src.errors.product import ProductException


class ProductVariantRepository:
    async def create_product_variant(self, product_variant_data, product_id, session: AsyncSession):
        if not product_variant_data:
            return
        
        if product_variant_data and isinstance(product_variant_data[0], dict):
            product_variant_data = [
                ProductVariantCreateModel(**item) for item in product_variant_data
            ]

        new_objects = []
        generated_skus = set()
        
        for item in product_variant_data:
            if item.sku:
                sku = item.sku
            else:
                while True:
                    sku = f"{str(product_id)[:8]}-{uuid.uuid4().hex[:6].upper()}"
                    if sku not in generated_skus:
                        break
                    
                generated_skus.add(sku)
                
            new_variant = Product_Variant(
                product_id=product_id,
                size=item.size,
                image=item.image,
                color_id=item.color_id if item.color_id else None,
                color_name=item.color_name if item.color_name else None,
                color_code=item.color_code if item.color_code else None,
                price=item.price,
                quantity=item.quantity,
                sku=sku,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            new_objects.append(new_variant)

        session.add_all(new_objects)
        await session.flush()


    async def get_all_product_variant(self, session: AsyncSession,
                                      select_columns: Optional[List[Any]] = None,
                                      joins: Optional[List[Tuple[Any, dict]]] = None,
                                      where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                      group_by_columns: Optional[List[Any]] = None,
                                      having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                      order_by: Optional[Any] = None,
                                      skip: int = 0,
                                      limit: int = 10,
                                      options: Optional[list] = None,
                                      for_update: bool = False):
        if select_columns is None:
            query = select(Product_Variant)
        else:
            query = select(*select_columns).select_from(Product_Variant)

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
            if isinstance(order_by, (list, tuple)):
                query = query.order_by(*order_by)
            else:
                query = query.order_by(order_by)

        if for_update:
            query = query.with_for_update()

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        variants = result.all()

        return variants, total

    async def get_stock_statuses_count(self, session: AsyncSession, warehouse_id: str) -> List[dict]:
        select_columns_summary = [
            Product_Variant.product_id,
            func.sum(Stock.available_quantity).label('total_available'),
            func.sum(
                func.cast(
                    and_(
                        Stock.quantity > 0,
                        Stock.min_stock_level.isnot(None),
                        Stock.available_quantity <= Stock.min_stock_level
                    ),
                    Integer
                )
            ).label('low_stock_variants'),
            func.sum(func.cast(Stock.quantity == 0, Integer)).label('out_of_stock_variants'),
            func.count(func.distinct(Product_Variant.id)).label('total_variants')
        ]
        stock_summary = (
            select(*select_columns_summary)
            .select_from(Product_Variant)
            .join(Stock, Stock.product_variant_id == Product_Variant.id)
            .where(
                and_(
                    Stock.warehouse_id == warehouse_id,
                    Product_Variant.deleted_at.is_(None)
                )
            )
            .group_by(Product_Variant.product_id)
        ).subquery()

        select_columns = [
            # Đếm products có hàng (available > 0 và không có variant nào low/out)
            func.sum(
                case(
                    (
                        and_(
                            stock_summary.c.total_available > 0,
                            stock_summary.c.low_stock_variants == 0,
                            stock_summary.c.out_of_stock_variants == 0
                        ),
                        1
                    ),
                    else_=0
                )
            ).label('available_count'),

            # Đếm products có ít nhất 1 variant sắp hết
            func.sum(
                case(
                    (stock_summary.c.low_stock_variants > 0, 1),
                    else_=0
                )
            ).label('low_count'),

            # Đếm products hết hàng hoàn toàn (tất cả variants đều hết)
            func.sum(
                case(
                    (
                        stock_summary.c.out_of_stock_variants == stock_summary.c.total_variants,
                        1
                    ),
                    else_=0
                )
            ).label('out_count')
        ]

        statement = (
            select(*select_columns)
            .select_from(stock_summary)
            .join(Product, Product.id == stock_summary.c.product_id)
            .where(Product.deleted_at.is_(None))
        )

        result = await session.exec(statement)
        row = result.one()

        return [
            {
                'value': 'available',
                'label': 'Đủ hàng',
                'count': int(row.available_count or 0)
            },
            {
                'value': 'low',
                'label': 'Sắp hết',
                'count': int(row.low_count or 0)
            },
            {
                'value': 'out',
                'label': 'Hết hàng',
                'count': int(row.out_count or 0)
            }
        ]


    async def get_product_variant(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession,
                                  joins: list = None):
        statement = select(Product_Variant).options(
            *joins if joins else []
        ).where(conditions)
        result = await session.exec(statement)

        return result.one_or_none()

    async def update_product_variant(self, update_data: dict, condition: ColumnElement[bool], session: AsyncSession):
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
