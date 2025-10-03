from datetime import datetime

from sqlalchemy.orm import joinedload
from sqlmodel import and_, desc

from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, Stock, Product_Variant
from src.errors.stock import StockException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import StockFilterParams

warehouse_repository = WareHouseRepository()
stock_repository = StockRepository()
product_variant_repository = ProductVariantRepository()

class GetStockByWarehouseService:
    async def get_stock_by_warehouse(self, warehouse_id: str, filters: StockFilterParams,
                                     session: AsyncSession, skip: int = 0, limit: int = 100):
        condition_warehouse = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        if filters.min_quantity and filters.max_quantity:
            if filters.min_quantity > filters.max_quantity:
                StockException.min_must_less_than_max()

        if filters.min_quantity is not None and filters.min_quantity < 0:
            StockException.min_must_greater_than_0()

        summary = await stock_repository.get_warehouse_summary(warehouse_id, session)

        condition_stocks = [Stock.warehouse_id == warehouse_id]

        if filters.status:
            condition_stocks.append(Stock.status == filters.status)

        if filters.min_quantity is not None:
            condition_stocks.append(Stock.quantity >= filters.min_quantity)

        if filters.max_quantity is not None:
            condition_stocks.append(Stock.quantity <= filters.max_quantity)

        if filters.low_stock_only:
            condition_stocks.append(
                and_(
                    Stock.min_stock_level.is_not(None),
                    Stock.quantity < Stock.min_stock_level,
                    Stock.quantity > 0
                )
            )

        elif filters.out_of_stock_only:
            condition_stocks.append(Stock.quantity == 0)

        order_by_stocks = desc(Stock.updated_at)

        joins = [
            joinedload(Stock.product_variant)
        ]

        stocks, total = await stock_repository.get_all_stocks(condition_stocks, session, 0, 1000, joins,
                                                              order_by_stocks)

        stock_items = []
        for stock in stocks:
            warehouse_name = warehouse.name
            warehouse_code = warehouse.code

            variant_sku = None
            if stock.product_variant and not stock.product_variant.deleted_at:
                variant_sku = stock.product_variant.sku

            if not variant_sku and stock.product_variant_id:
                condition_sku = and_(
                    Product_Variant.id == stock.product_variant_id,
                    Product_Variant.deleted_at.is_(None)
                )
                variant = await product_variant_repository.get_product_variant(condition_sku, session)
                variant_sku = variant.sku if variant else None

            stock_items.append({
                "id": str(stock.id),
                "warehouse_id": str(stock.warehouse_id),
                "warehouse_name": warehouse_name,
                "warehouse_code": warehouse_code,
                "product_variant_id": str(stock.product_variant_id),
                "product_variant_sku": variant_sku,
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

        warehouse_info = {
            "id": str(warehouse.id),
            "name": warehouse.name,
            "code": warehouse.code,
            "address": warehouse.address,
            "is_active": warehouse.is_active,
            "is_default": warehouse.is_default
        }

        return {
            "warehouse": warehouse_info,
            "total_products": summary.get("total_products", 0),
            "total_quantity": summary.get("total_quantity", 0),
            "total_available_quantity": summary.get("total_available_quantity", 0),
            "total_reserved_quantity": summary.get("total_reserved_quantity", 0),
            "total_inventory_value": summary.get("total_inventory_value", 0),
            "low_stock_items": summary.get("low_stock_items", 0),
            "out_of_stock_items": summary.get("out_of_stock_items", 0),
            "stock_items": stock_items,
            "total": total,
        }




