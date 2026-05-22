from datetime import datetime
from typing import Optional

from src.cache import cache_service
from src.crud.purchase_return.services.utils_service import UtilsPRService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.stock.repositories import StockRepository
from src.crud.stock.services.adjust_stock_for_pr import AdjustForPR
from src.database.models import PurchaseReturn, Stock
from src.errors.purchase_return import PurchaseReturnException
import logging

from src.errors.stock import StockException

logger = logging.getLogger(__name__)

utils_pr_service = UtilsPRService()
stock_repository = StockRepository()
adjust_stock_for_pr_service = AdjustForPR()


class CompletePurchaseReturnService:
    async def complete_purchase_return(self, session: AsyncSession, purchase_return_id: str, 
                                       completed_by: Optional[str] = None):
        pr = await utils_pr_service.validate_and_get_pr(session, purchase_return_id)

        if pr.status != "confirmed":
            PurchaseReturnException.only_complete_when_confirmed()

        if not pr.return_details or len(pr.return_details) == 0:
            PurchaseReturnException.no_return_details_found()
            
        try:
            pr.status = "completed"
            pr.completed_at = datetime.now()
            pr.shipped_date = datetime.now()
            pr.completed_by = completed_by
            pr.updated_at = datetime.now()
            session.add(pr)

            await session.flush()
            
            gr_detail_ids = list({
                str(d.goods_receipt_detail_id) 
                for d in pr.return_details 
                if d.goods_receipt_detail_id
            })
            
            if gr_detail_ids:
                await utils_pr_service.batch_sync_returned_quantities(session, gr_detail_ids)
            
            if pr.warehouse_id:
                await self.adjust_stock_for_return(session, pr, completed_by)

                await cache_service.delete(f"stock:warehouse:{str(pr.warehouse_id)}:summary")
                await cache_service.delete_pattern(f"stock:low_stock:warehouse:{str(pr.warehouse_id)}:*")
                await cache_service.delete(f"stock:warehouse:{str(pr.warehouse_id)}:filters")

                logger.info(f"Invalidated stock caches for warehouse {pr.warehouse_id} after purchase return")
            
            await session.commit()
            await session.refresh(pr)

            return {
                "id": str(pr.id),
                "return_number": pr.return_number,
                "status": pr.status,
                "shipped_date": pr.shipped_date.isoformat() if pr.shipped_date else None,
                "completed_at": pr.completed_at.isoformat(),
                "affected_items": len(pr.return_details),
                "total_return_amount": pr.total_return_amount
            }
            
        except Exception as e:
            await session.rollback()
            logger.error("Error complete purchase return: ", e)
            PurchaseReturnException.error_while_complete_pr()
            
            
    async def adjust_stock_for_return(self, session: AsyncSession, pr: PurchaseReturn, performed_by: Optional[str]):
        warehouse_id = str(pr.warehouse_id)
        
        variant_quantities = {}
        for detail in pr.return_details:
            variant_id = str(detail.product_variant_id)
            
            if variant_id not in variant_quantities:
                variant_quantities[variant_id] = {
                    'quantity': 0,
                    'unit_cost': detail.unit_cost,
                    'total_cost': 0
                }
                
            variant_quantities[variant_id]['quantity'] += detail.return_quantity
            variant_quantities[variant_id]['total_cost'] += detail.total_cost
        
        variant_ids = list(variant_quantities.keys())
        conditions = [
            Stock.warehouse_id == warehouse_id,
            Stock.product_variant_id.in_(variant_ids)
        ]    

        stocks = await stock_repository.get_all_stocks(session=session, where_conditions=conditions)
        stocks_map = {str(stock.product_variant_id): stock for stock in stocks}
        
        for variant_id, data in variant_quantities.items():
            stock = stocks_map.get(variant_id)
            
            if not stock:
                StockException.no_inventory_for_product_at_warehouse(variant_id, warehouse_id)
                
            if stock.quantity < data['quantity']:
                StockException.insufficient_inventory_to_fulfill_order(variant_id, stock.quantity, data['quantity'])
                
            await adjust_stock_for_pr_service.adjust_stock_for_purchase_return(
                session=session,
                warehouse_id=warehouse_id,
                product_variant_id=variant_id,
                quantity_to_return=data['quantity'],
                unit_cost=data['unit_cost'],
                reference_id=str(pr.id),
                reference_type="purchase_return",
                reason=f"Hoàn trả hàng cho NCC - PR#{pr.return_number} - Lý do: {pr.return_reason}",
                performed_by=performed_by
            )
                
