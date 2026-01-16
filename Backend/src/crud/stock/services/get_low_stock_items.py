from typing import Optional, Dict
from sqlalchemy.orm import selectinload
from sqlmodel import asc
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Stock, Product_Variant
from src.schemas.stock import LowStockQueryParams

warehouse_repository = WareHouseRepository()
stock_repository = StockRepository()
product_variant_repository = ProductVariantRepository()


class GetLowStockItemsService:
    async def get_low_stock_items(self, session: AsyncSession, params: LowStockQueryParams,
                                  skip: int = 0, limit: int = 20):
        condition_stocks = [
            Stock.available_quantity < Stock.min_stock_level,
            Stock.min_stock_level.isnot(None),
            Stock.status == "available"
        ]

        if params.warehouse_id:
            condition_stocks.append(Stock.warehouse_id == params.warehouse_id)

        options = [
            selectinload(Stock.warehouse),
            selectinload(Stock.product_variant).selectinload(Product_Variant.product),
            selectinload(Stock.product_variant).selectinload(Product_Variant.color)
        ]

        order_by = asc(Stock.available_quantity / Stock.min_stock_level)

        stocks, total = await stock_repository.get_all_stocks(
            session=session,
            where_conditions=condition_stocks,
            order_by=order_by,
            skip=skip,
            limit=limit,
            options=options
        )

        items = []
        for stock in stocks:
            item = self.build_low_stock_item(stock)

            if params.severity and item['severity'] != params.severity:
                continue

            items.append(item)
            
        return {
            "data": items,
            "total": total
        }

    def determine_severity(self, available_quantity: int, shortage_percentage: float) -> str:
        if available_quantity == 0:
            return "critical"
        elif shortage_percentage >= 80:
            return "high"
        elif shortage_percentage >= 50:
            return "medium"
        else:
            return "low"

    def get_variant_color(self, stock) -> tuple[Optional[str], Optional[str]]:
        if not stock.product_variant:
            return None, None

        if stock.product_variant.color_name:
            return stock.product_variant.color_name, stock.product_variant.color_code
        elif stock.product_variant.color:
            return stock.product_variant.color.name, stock.product_variant.color.code

        return None, None

    def build_low_stock_item(self, stock) -> Dict:
        shortage = stock.min_stock_level - stock.available_quantity
        shortage_percentage = (
                shortage / stock.min_stock_level * 100
        ) if stock.min_stock_level > 0 else 0

        severity = self.determine_severity(stock.available_quantity, shortage_percentage)
        variant_color_name, variant_color_code = self.get_variant_color(stock)

        return {
            "stock_id": str(stock.id),
            "warehouse_id": str(stock.warehouse_id),
            "warehouse_name": stock.warehouse.name if stock.warehouse else None,
            "warehouse_code": stock.warehouse.code if stock.warehouse else None,
            "product_variant_id": str(stock.product_variant_id),
            "product_name": (
                stock.product_variant.product.name
                if stock.product_variant and stock.product_variant.product
                else None
            ),
            "variant_sku": stock.product_variant.sku if stock.product_variant else None,
            "variant_size": stock.product_variant.size if stock.product_variant else None,
            "variant_color_name": variant_color_name,
            "variant_color_code": variant_color_code,
            "variant_image": stock.product_variant.image if stock.product_variant else None,
            "available_quantity": stock.available_quantity,
            "reserved_quantity": stock.reserved_quantity,
            "total_quantity": stock.quantity,
            "min_stock_level": stock.min_stock_level,
            "shortage": shortage,
            "shortage_percentage": round(shortage_percentage, 2),
            "severity": severity,
            "cost_price": float(stock.cost_price) if stock.cost_price else None,
            "last_inbound_date": stock.last_inbound_date.isoformat() if stock.last_inbound_date else None,
            "last_outbound_date": stock.last_outbound_date.isoformat() if stock.last_outbound_date else None
        }
