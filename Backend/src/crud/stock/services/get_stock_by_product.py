from datetime import datetime

from sqlalchemy.orm import joinedload
from sqlmodel import and_, desc

from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, Stock, Product_Variant
from src.errors.product import ProductException
from src.errors.stock import StockException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import StockFilterParams

warehouse_repository = WareHouseRepository()
stock_repository = StockRepository()
product_variant_repository = ProductVariantRepository()


class GetStockByProductService:
    async def get_stock_by_product(self, variant_id: str, session: AsyncSession,
                                   skip: int = 0, limit: int = 100):
        condition_variant = and_(
            Product_Variant.id == variant_id,
            Product_Variant.deleted_at.is_(None)
        )
        variant = await product_variant_repository.get_product_variant(condition_variant, session)
        if not variant:
            ProductException.not_found_variant()

        summary = await stock_repository.get_product_summary(variant_id, session)

        condition_stocks = [Stock.product_variant_id == variant_id]
        order_by_stocks = desc(Stock.quantity)
        joins = [
            joinedload(Stock.warehouse)
        ]
        stocks, total = await stock_repository.get_all_stocks(condition_stocks, skip=skip, limit=limit, session=session,
                                                              joins=joins, order_by_clause=order_by_stocks)

        stock_by_warehouse = []
        for stock in stocks:
            warehouse_name = None
            warehouse_code = None

            if stock.warehouse and not stock.warehouse.deleted_at:
                warehouse_name = stock.warehouse.name
                warehouse_code = stock.warehouse.code
            else:
                condition_wh = and_(
                    Warehouse.id == stock.warehouse_id,
                    Warehouse.deleted_at.is_(None)
                )
                warehouse = await warehouse_repository.get_warehouse(condition_wh, session)
                if warehouse:
                    warehouse_name = warehouse.name
                    warehouse_code = warehouse.code

            stock_by_warehouse.append({
                "id": str(stock.id),
                "warehouse_id": str(stock.warehouse_id),
                "warehouse_name": warehouse_name,
                "warehouse_code": warehouse_code,
                "product_variant_id": str(stock.product_variant_id),
                "product_variant_sku": variant.sku,
                "quantity": stock.quantity,
                "reserved_quantity": stock.reserved_quantity,
                "available_quantity": stock.available_quantity,
                "min_stock_level": stock.min_stock_level,
                "max_stock_level": stock.max_stock_level,
                "cost_price": stock.cost_price,
                "last_cost_price": stock.last_cost_price,
                "status": stock.status.value if hasattr(stock.status, 'value') else str(stock.status),
                "last_inbound_date": stock.last_inbound_date.isoformat() if stock.last_inbound_date else None,
                "last_outbound_date": stock.last_outbound_date.isoformat() if stock.last_outbound_date else None,
                "updated_at": stock.updated_at.isoformat() if stock.updated_at else None
            })

        return {
            "product_variant_id": str(variant_id),
            "product_variant_sku": variant.sku,
            "total_quantity_all_warehouses": summary.get("total_quantity", 0),
            "total_available_quantity": summary.get("total_available_quantity", 0),
            "total_reserved_quantity": summary.get("total_reserved_quantity", 0),
            "warehouses_count": summary.get("warehouses_count", 0),
            "average_cost_price": summary.get("average_cost_price", 0),
            "stock_by_warehouse": stock_by_warehouse,
            "total": total,
        }
