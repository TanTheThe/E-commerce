from datetime import datetime, timedelta
from typing import Optional
from unittest import skip
from sqlalchemy.orm import selectinload
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Stock, Product_Variant, StockTransaction
from src.errors.stock import StockException

warehouse_repository = WareHouseRepository()
stock_repository = StockRepository()
product_variant_repository = ProductVariantRepository()


class GetStockDetailService:
    async def get_low_stock_items(self, stock_id: str, session: AsyncSession):
        condition_stock = [
            Stock.id == stock_id
        ]

        option_stock = [
            selectinload(Stock.warehouse),
            selectinload(Stock.product_variant).selectinload(Product_Variant.product),
            selectinload(Stock.product_variant).selectinload(Product_Variant.color)
        ]

        stock = await stock_repository.get_stock(
            session=session,
            where_conditions=condition_stock,
            options=option_stock
        )
        
        if not stock:
            StockException.stock_not_found()
            
        condition_transaction = [
            StockTransaction.stock_id == stock_id
        ]
        
        option_transaction = [
            selectinload(StockTransaction.user),
            selectinload(StockTransaction.warehouse)
        ]
        
        transactions, total = await stock_repository.get_all_stock_transactions(
            session=session,
            where_conditions=condition_transaction,
            skip=0,
            limit=10,
            options=option_transaction
        )

        transaction_responses = []
        for txn in transactions:
            transaction_responses.append(
                {
                    "id": str(txn.id),
                    "transaction_type": txn.transaction_type,
                    "quantity": txn.quantity,
                    "previous_quantity": txn.previous_quantity,
                    "new_quantity": txn.new_quantity,
                    "unit_cost": txn.unit_cost,
                    "total_cost": txn.total_cost,
                    "reference_id": str(txn.reference_id),
                    "reference_type": txn.reference_type,
                    "reason": txn.reason,
                    "note": txn.note,
                    "performed_by": txn.performed_by,
                    "performed_by_name": txn.user.first_name + txn.user.last_name if txn.user else None,
                    "created_at": txn.created_at
                }
            )
            
        thirty_days_ago = datetime.now() - timedelta(days=30)
        total_inbound = 0
        total_outbound = 0
        
        for txn in transactions:
            if txn.created_at >= thirty_days_ago:
                if txn.transaction_type == 'inbound':
                    total_inbound += txn.quantity
                elif txn.transaction_type == 'outbound':
                    total_outbound += abs(txn.quantity)
        
        avg_daily_outbound = total_outbound / 30 if total_outbound > 0 else 0
        
        estimated_days_remaining = None
        if avg_daily_outbound > 0:
            estimated_days_remaining = int(stock.available_quantity / avg_daily_outbound)
            
        
        return {
            "stock_id": str(stock.id),
            "warehouse_id": str(stock.warehouse_id),
            "warehouse_name": stock.warehouse.name if stock.warehouse else None,
            "warehouse_code": stock.warehouse.code if stock.warehouse else None,
            "product_variant_id": str(stock.product_variant_id),
            "product_name": stock.product_variant.product.name if stock.product_variant and stock.product_variant.product else None,
            "variant_sku": stock.product_variant.sku if stock.product_variant else None,
            "variant_size": stock.product_variant.size if stock.product_variant else None,
            "variant_color_name": stock.product_variant.color_name if stock.product_variant else None,
            "variant_color_code": stock.product_variant.color_code if stock.product_variant else None,
            "variant_image": stock.product_variant.image if stock.product_variant else None,
            "variant_price": stock.product_variant.price if stock.product_variant else None,
            "available_quantity": stock.available_quantity,
            "reserved_quantity": stock.reserved_quantity,
            "total_quantity": stock.quantity,
            "min_stock_level": stock.min_stock_level,
            "max_stock_level": stock.max_stock_level,
            "cost_price": stock.cost_price,
            "last_cost_price": stock.last_cost_price,
            "status": stock.status,
            "last_inbound_date": stock.last_inbound_date,
            "last_outbound_date": stock.last_outbound_date,
            "created_at": str(stock.created_at),
            "updated_at": str(stock.updated_at),
            "recent_transactions": transaction_responses,
            "total_inbound": total_inbound,
            "total_outbound": total_outbound,
            "avg_daily_outbound": round(avg_daily_outbound, 2),
            "estimated_days_remaining": estimated_days_remaining
        }