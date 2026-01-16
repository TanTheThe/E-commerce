from sqlalchemy import func, case
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product.repositories import ProductRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import Warehouse, Product_Variant, Stock, Product
from src.errors.warehouse import WareHouseException

warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
stock_repository = StockRepository()
category_product_repository = CategoriesProductRepository()
product_repository = ProductRepository()

class GetWarehouseSummaryService:
    async def get_warehouse_summary(self, session: AsyncSession, warehouse_id: str):
        condition_warehouse = [
            Warehouse.id == warehouse_id,
            Warehouse.is_active == True
        ]
        warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition_warehouse)
        if not warehouse:
            WareHouseException.warehouse_not_found()

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
            ).label('low_stock_variants'),  # Số variant sắp hết hàng (còn hàng nhưng <= min_stock_level)

            func.sum(
                case(
                    (Stock.quantity == 0, 1),
                    else_=0
                )
            ).label('out_of_stock_variants'),  # # Số variant hết hàng hoàn toàn

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
            ).label('low_stock_products'),  # Số product có ít nhất 1 variant sắp hết

            func.count(
                func.distinct(
                    case(
                        (Stock.quantity == 0, Product_Variant.product_id),
                        else_=None
                    )
                )
            ).label('out_of_stock_products')  # Số product hết hàng hoàn toàn (tất cả variants đều hết)
        ]

        joins = [
            (
                Product_Variant,
                {
                    'on': Stock.product_variant_id == Product_Variant.id
                }
            ),
            (
                Product,
                {
                    'on': Product_Variant.product_id == Product.id
                }
            )
        ]

        where_conditions = [
            Stock.warehouse_id == warehouse_id,
            Product_Variant.deleted_at.is_(None),
            Product.deleted_at.is_(None)
        ]

        row = await stock_repository.get_stock(
            session=session,
            select_columns=select_columns,
            joins=joins,
            where_conditions=where_conditions
        )

        if not row:
            summary = {
                'total_products': 0,
                'total_variants': 0,
                'total_quantity': 0,
                'total_value': 0,
                'low_stock_products': 0,
                'low_stock_variants': 0,
                'out_of_stock_products': 0,
                'out_of_stock_variants': 0
            }
        else:
            summary = {
                'total_products': int(row.total_products or 0),
                'total_variants': int(row.total_variants or 0),
                'total_quantity': int(row.total_quantity or 0),
                'total_value': int(row.total_value or 0),
                'low_stock_products': int(row.low_stock_products or 0),
                'low_stock_variants': int(row.low_stock_variants or 0),
                'out_of_stock_products': int(row.out_of_stock_products or 0),
                'out_of_stock_variants': int(row.out_of_stock_variants or 0)
            }

        return {
            "warehouse": {
                "id": str(warehouse.id),
                "name": warehouse.name,
                "code": warehouse.code
            },
            "summary": summary
        }







