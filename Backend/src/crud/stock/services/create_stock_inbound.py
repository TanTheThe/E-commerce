from datetime import datetime

from sqlalchemy.orm import joinedload
from sqlmodel import and_, desc

from src.crud.product.repositories import ProductRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Product, Warehouse, Stock, Product_Variant
from src.errors.product import ProductException
from src.errors.stock import StockException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import StockFilterParams, StockInboundCreate

warehouse_repository = WareHouseRepository()
stock_repository = StockRepository()
product_variant_repository = ProductVariantRepository()
product_repository = ProductRepository()


class CreateStockInboundService:
    async def create_inbound(self, inbound_data: StockInboundCreate, session: AsyncSession):
        condition = and_(Warehouse.id == inbound_data.warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        items_result = []
        total_items = len(inbound_data.items)
        total_quantity = 0
        total_cost = 0

        for item in inbound_data.items:
            condition_variant = and_(
                Product_Variant.id == item.product_variant_id, Product_Variant.deleted_at.is_(None))
            variant = await product_variant_repository.get_product_variant(condition_variant, session)
            if not variant:
                ProductException.not_found_variant()

            condition_product = and_(Product.id == variant.product_id, Product.deleted_at.is_(
                None), Product.status == "active")
            product = await product_repository.get_product(condition_product, session)
            if not product:
                ProductException.not_found_product_from_variant()

            condition_stock = and_(Stock.warehouse_id == inbound_data.warehouse_id,
                                   Stock.product_variant_id == item.product_variant_id)
            stock = await stock_repository.get_stock(condition_stock, session)

            if not stock:
                stock_dict = {
                    "warehouse_id": inbound_data.warehouse_id,
                    "product_variant_id": item.product_variant_id,
                    "quantity": 0,
                    "reserved_quantity": 0,
                    "available_quantity": 0,
                    "status": "available",
                    "created_at": datetime.now()
                }
                stock = await stock_repository.create_stock(stock_dict, session)

            previous_quantity = stock.quantity

            item_total_cost = item.unit_cost * item.quantity

            current_total_value = (stock.cost_price or 0) * stock.quantity

            new_total_value = item.unit_cost * item.quantity

            new_quantity = stock.quantity + item.quantity

            if new_quantity > 0:
                new_cost_price = round(
                    (current_total_value + new_total_value) / new_quantity,
                    2
                )
            else:
                new_cost_price = item.unit_cost

            condition = and_(Stock.id == stock.id)
            await stock_repository.update_stock(condition, {
                "quantity": new_quantity,
                "available_quantity": new_quantity - stock.reserved_quantity,
                "cost_price": new_cost_price,
                "last_cost_price": item.unit_cost,
                "last_inbound_date": datetime.now(),
                "updated_at": datetime.now()
            }, session)

            stock_transaction_dict = {
                "warehouse_id": inbound_data.warehouse_id,
                "stock_id": stock.id,
                "variant_id": item.product_variant_id,
                "quantity": item.quantity,
                "previous_quantity": previous_quantity,
                "new_quantity": new_quantity,
                "unit_cost": item.unit_cost,
                "total_cost": item_total_cost,
                "reason": inbound_data.reason,
                "note": item.note or inbound_data.note,
                "performed_by": inbound_data.performed_by
            }
            await stock_repository.create_stock_transaction(stock_transaction_dict, session)

            items_result.append({
                "product_variant_id": item.product_variant_id,
                "product_name": product.name,
                "sku": variant.sku,
                "size": variant.size,
                "color_name": variant.color_name,
                "quantity": item.quantity,
                "unit_cost": item.unit_cost,
                "total_cost": item_total_cost,
                "previous_quantity": previous_quantity,
                "new_quantity": new_quantity
            })

            total_quantity += item.quantity
            total_cost += item_total_cost

        await session.commit()

        return {
            "warehouse_id": inbound_data.warehouse_id,
            "warehouse_name": warehouse.name,
            "total_items": total_items,
            "total_quantity": total_quantity,
            "total_cost": total_cost,
            "items": items_result,
            "reason": inbound_data.reason,
            "note": inbound_data.note,
            "performed_by": inbound_data.performed_by,
            "created_at": datetime.now()
        }
