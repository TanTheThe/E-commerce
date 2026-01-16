from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import selectinload
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.stock_transaction.repositories import StockTransactionRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Stock, Product_Variant, StockTransaction
from src.errors.stock import StockException

warehouse_repository = WareHouseRepository()
stock_repository = StockRepository()
product_variant_repository = ProductVariantRepository()
stock_transaction_repository = StockTransactionRepository()


class GetStockDetailService:
    TRANSACTION_LIMIT = 100  # Limit cho recent transactions
    ANALYTICS_DAYS = 30  # Số ngày để tính analytics

    async def get_stock_detail(self, stock_id: str, session: AsyncSession):
        condition_stock = [Stock.id == stock_id]
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

        condition_transaction = [StockTransaction.stock_id == stock_id]
        option_transaction = [
            selectinload(StockTransaction.user),
            selectinload(StockTransaction.warehouse)
        ]

        transactions, total_transactions = await stock_transaction_repository.get_all_stock_transactions(
            session=session,
            where_conditions=condition_transaction,
            skip=0,
            limit=1000,
            options=option_transaction
        )

        transaction_responses = [
            self.build_transaction_response(txn)
            for txn in transactions[:self.TRANSACTION_LIMIT]
        ]

        analytics = self.calculate_analytics(transactions)

        estimated_days_remaining = self.estimate_days_remaining(
            stock.available_quantity,
            analytics['avg_daily_outbound']
        )

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
            "variant_price": float(
                stock.product_variant.price) if stock.product_variant and stock.product_variant.price else None,
            "available_quantity": stock.available_quantity,
            "reserved_quantity": stock.reserved_quantity,
            "total_quantity": stock.quantity,
            "min_stock_level": stock.min_stock_level,
            "max_stock_level": stock.max_stock_level,
            "cost_price": float(stock.cost_price) if stock.cost_price else None,
            "last_cost_price": float(stock.last_cost_price) if stock.last_cost_price else None,
            "status": stock.status,
            "last_inbound_date": stock.last_inbound_date.isoformat() if stock.last_inbound_date else None,
            "last_outbound_date": stock.last_outbound_date.isoformat() if stock.last_outbound_date else None,
            "created_at": stock.created_at.isoformat() if stock.created_at else None,
            "updated_at": stock.updated_at.isoformat() if stock.updated_at else None,
            "total_inbound_30d": analytics['total_inbound'],
            "total_outbound_30d": analytics['total_outbound'],
            "avg_daily_outbound": analytics['avg_daily_outbound'],
            "estimated_days_remaining": estimated_days_remaining,
            "recent_transactions": transaction_responses,
            "total_transactions": total_transactions
        }

    def get_variant_color(self, stock) -> tuple[Optional[str], Optional[str]]:
        if not stock.product_variant:
            return None, None

        if stock.product_variant.color_name:
            return stock.product_variant.color_name, stock.product_variant.color_code
        elif stock.product_variant.color:
            return stock.product_variant.color.name, stock.product_variant.color.code

        return None, None

    def build_transaction_response(self, txn) -> Dict:
        performed_by_name = None
        if txn.user:
            first_name = txn.user.first_name or ""
            last_name = txn.user.last_name or ""
            performed_by_name = f"{first_name} {last_name}".strip() or None

        return {
            "id": str(txn.id),
            "transaction_type": txn.transaction_type,
            "quantity": txn.quantity,
            "previous_quantity": txn.previous_quantity,
            "new_quantity": txn.new_quantity,
            "unit_cost": float(txn.unit_cost) if txn.unit_cost else None,
            "total_cost": float(txn.total_cost) if txn.total_cost else None,
            "reference_id": str(txn.reference_id) if txn.reference_id else None,
            "reference_type": txn.reference_type,
            "reason": txn.reason,
            "note": txn.note,
            "performed_by": str(txn.performed_by),
            "performed_by_name": performed_by_name,
            "created_at": txn.created_at.isoformat() if txn.created_at else None
        }

    def calculate_analytics(self, transactions: List) -> Dict:
        """Tính toán analytics từ transactions trong 30 ngày"""
        thirty_days_ago = datetime.now() - timedelta(days=self.ANALYTICS_DAYS)

        total_inbound = 0
        total_outbound = 0

        for txn in transactions:
            if txn.created_at and txn.created_at >= thirty_days_ago:
                if txn.transaction_type == 'inbound':
                    total_inbound += txn.quantity
                elif txn.transaction_type == 'outbound':
                    total_outbound += abs(txn.quantity)

        avg_daily_outbound = total_outbound / self.ANALYTICS_DAYS if total_outbound > 0 else 0

        return {
            "total_inbound": total_inbound,
            "total_outbound": total_outbound,
            "avg_daily_outbound": round(avg_daily_outbound, 2)
        }

    def estimate_days_remaining(self, available_quantity: int, avg_daily_outbound: float) -> Optional[int]:
        """Ước tính số ngày còn lại trước khi hết hàng"""
        if avg_daily_outbound > 0:
            return int(available_quantity / avg_daily_outbound)
        return None

