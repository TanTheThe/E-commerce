from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from src.database.models import Stock, Product_Variant, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, case
from datetime import datetime


class StockRepository:
    async def get_warehouse_summary(self, warehouse_id: str, session: AsyncSession) -> dict:
        select_columns = [
            func.count(func.distinct(Product_Variant.product_id)).label('total_products'),

            func.count(func.distinct(Product_Variant.id)).label('total_variants'),

            func.sum(Stock.quantity).label('total_quantity'),

            func.sum(
                Stock.quantity * func.coalesce(Stock.cost_price, 0)
            ).label('total_value'),

            func.sum(
                case(
                    (
                        and_(
                            Stock.quantity > 0,
                            Stock.min_stock_level.isnot(None),
                            Stock.available_quantity <= Stock.min_stock_level
                        ),
                        1
                    ),
                    else_=0
                )
            ).label('low_stock_variants'),      # Số variant sắp hết hàng (còn hàng nhưng <= min_stock_level)

            func.sum(
                case(
                    (Stock.quantity == 0, 1),
                    else_=0
                )
            ).label('out_of_stock_variants'),   # # Số variant hết hàng hoàn toàn

            func.count(
                func.distinct(
                    case(
                        (
                            and_(
                                Stock.quantity > 0,
                                Stock.min_stock_level.isnot(None),
                                Stock.available_quantity <= Stock.min_stock_level
                            ),
                            Product_Variant.product_id
                        ),
                        else_=None
                    )
                )
            ).label('low_stock_products'),      # Số product có ít nhất 1 variant sắp hết

            func.count(
                func.distinct(
                    case(
                        (Stock.quantity == 0, Product_Variant.product_id),
                        else_=None
                    )
                )
            ).label('out_of_stock_products')    # Số product hết hàng hoàn toàn (tất cả variants đều hết)
        ]

        statement = (
            select(*select_columns)
            .select_from(Stock)
            .join(Product_Variant, Stock.product_variant_id == Product_Variant.id)
            .join(Product, Product_Variant.product_id == Product.id)
            .where(
                and_(
                    Stock.warehouse_id == warehouse_id,
                    Product_Variant.deleted_at.is_(None),
                    Product.deleted_at.is_(None)
                )
            )
        )

        result = await session.exec(statement)
        row = result.one()

        return {
            'total_products': int(row.total_products or 0),
            'total_variants': int(row.total_variants or 0),
            'total_quantity': int(row.total_quantity or 0),
            'total_value': int(row.total_value or 0),
            'low_stock_products': int(row.low_stock_products or 0),
            'low_stock_variants': int(row.low_stock_variants or 0),
            'out_of_stock_products': int(row.out_of_stock_products or 0),
            'out_of_stock_variants': int(row.out_of_stock_variants or 0)
        }


    async def get_all_stocks(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None,
                             for_update: bool = False):

        if select_columns is None:
            query = select(Stock)
        else:
            query = select(*select_columns).select_from(Stock)

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

        if for_update:
            query = query.with_for_update()

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        stocks = result.all()

        return stocks, total


    async def get_stock(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            options: Optional[list] = None,
                            for_update: bool = False):

        if select_columns is None:
            query = select(Stock)
        else:
            query = select(*select_columns).select_from(Stock)

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

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        if for_update:
            query = query.with_for_update()

        result = await session.exec(query)
        stock = result.one_or_none()

        return stock


    async def create_stock(self, stock_data: dict, session: AsyncSession):
        stock = Stock(
            **stock_data,
            created_at=datetime.now()
        )
        session.add(stock)

        return stock


    async def update_stock(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Stock)
            .where(condition)
            .values(**values)
        )

        await session.exec(stmt)
