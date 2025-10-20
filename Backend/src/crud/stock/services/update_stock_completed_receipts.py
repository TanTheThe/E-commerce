from datetime import datetime
from decimal import Decimal
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.stock.repositories import StockRepository
from src.crud.stock.services.utils_service import UtilsStockService
from src.crud.stock_transaction.repositories import StockTransactionRepository
from src.database.models import Stock


goods_receipt_repository = GoodsReceiptRepository()
stock_repository = StockRepository()
stock_transaction_repository = StockTransactionRepository()
utils_stock_service = UtilsStockService()


class StockUpdateCompletedReceiptService:
    async def update_stock_for_completed_receipts(self, all_related_grs: list, warehouse_id: str,
                                                  approved_by: str, session: AsyncSession) -> list:
        stock_updates = []

        variant_totals = self.aggregate_variant_quantities(all_related_grs)

        variant_ids = list(variant_totals.keys())
        if not variant_ids:
            return stock_updates

        stocks_map = await self.get_existing_stocks_with_lock(session, warehouse_id, variant_ids)

        for variant_id, data in variant_totals.items():
            if data['total_quantity'] <= 0:
                continue
        
            stock_update = await self.update_single_variant_stock(
                session=session,
                warehouse_id=warehouse_id,
                variant_id=variant_id,
                data=data,
                stocks_map=stocks_map,
                approved_by=approved_by
            )
            
            if stock_update:
                stock_updates.append(stock_update)

        return stock_updates
            
    async def aggregate_variant_quantities(self, all_related_grs: list, session: AsyncSession):
        variant_totals = {}

        for gr in all_related_grs:
            for detail in gr.receipt_details:
                variant_id = str(detail.product_variant_id)

                if variant_id not in variant_totals:
                    variant_totals[variant_id] = {
                        'total_quantity': 0,
                        'gr_details': []
                    }

                variant_totals[variant_id]['total_quantity'] += detail.accepted_quantity
                variant_totals[variant_id]['gr_details'].append({
                    'gr_id': str(gr.id),
                    'gr_number': gr.receipt_number,
                    'quantity': detail.accepted_quantity,
                    'unit_cost': detail.unit_cost if hasattr(detail, 'unit_cost') else None
                })

        return variant_totals

    async def get_existing_stocks_with_lock(self, session: AsyncSession, warehouse_id: str,
                                            variant_ids: list):
        condition_stocks = [
            Stock.warehouse_id == warehouse_id,
            Stock.product_variant_id.in_(variant_ids)
        ]

        existing_stocks = await stock_repository.get_all_stocks(
            session=session,
            where_conditions=condition_stocks,
            for_update=True
        )

        return {str(stock.product_variant_id): stock for stock in existing_stocks}
    
    async def update_single_variant_stock(self, session: AsyncSession, warehouse_id: str, variant_id: str,
                                          data: dict, stocks_map: dict, approved_by: str):
        stock = stocks_map.get(variant_id)
        
        if not stock:
            stock = await self.create_new_stock(session, warehouse_id, variant_id)
            
        previous_quantity = stock.quantity
        new_quantity = previous_quantity + data['total_quantity']
        
        new_cost_price, avg_unit_cost = utils_stock_service.calculate_weighted_average_cost(
            stock=stock,
            previous_quantity=previous_quantity,
            new_data=data
        )
        
        stock.quantity = new_quantity
        stock.available_quantity = new_quantity - (stock.reserved_quantity or 0)
        
        if new_cost_price:
            stock.cost_price = float(new_cost_price)
            stock.last_cost_price = float(avg_unit_cost)
            
        stock.last_inbound_date = datetime.now()
        stock.updated_at = datetime.now()
        
        stock.status = utils_stock_service.determine_stock_status(stock)
        
        await self.create_stock_transactions(
            session=session,
            stock=stock,
            warehouse_id=warehouse_id,
            variant_id=variant_id,
            gr_details=data['gr_details'],
            approved_by=approved_by,
            running_quantity=previous_quantity
        )

        return {
            'variant_id': variant_id,
            'total_quantity_added': data['total_quantity'],
            'previous_stock': previous_quantity,
            'new_stock': new_quantity,
            'cost_price': float(new_cost_price) if new_cost_price else None,
            'status': stock.status
        }
            
    async def create_new_stock(self, session: AsyncSession, warehouse_id: str, variant_id: str):
        stock_dict = {
            "warehouse_id": warehouse_id,
            "product_variant_id": variant_id,
            "quantity": 0,
            "reserved_quantity": 0,
            "available_quantity": 0,
            "status": "available",
            "cost_price": None,
            "last_cost_price": None,
            "created_at": datetime.now()
        }
        stock = await stock_repository.create_stock(
            session=session, 
            stock_data=stock_dict
        )
        await session.flush()
        return stock
    
    async def create_stock_transactions(self, session: AsyncSession, stock, warehouse_id: str, variant_id: str,
                                        gr_details: list, approved_by: str, running_quantity: int):
        for gr_detail in gr_details:
            if gr_detail['quantity'] <= 0:
                continue

            unit_cost = gr_detail['unit_cost']
            quantity = gr_detail['quantity']

            transaction_data = {
                "warehouse_id": warehouse_id,
                "stock_id": str(stock.id),
                "product_variant_id": variant_id,
                "transaction_type": "inbound",
                "quantity": quantity,
                "previous_quantity": running_quantity,
                "new_quantity": running_quantity + quantity,
                "unit_cost": float(unit_cost) if unit_cost else None,
                "total_cost": float(Decimal(str(unit_cost)) * Decimal(str(quantity))) if unit_cost else None,
                "reference_id": gr_detail['gr_id'],
                "reference_type": "goods_receipt",
                "reason": f"Nhập hàng từ phiếu {gr_detail['gr_number']}",
                "performed_by": approved_by,
                "transaction_date": datetime.now(),
            }

            await stock_transaction_repository.create_stock_transaction(
                transaction_data, 
                session=session
            )

            running_quantity += quantity
    