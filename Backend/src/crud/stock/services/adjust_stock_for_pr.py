from datetime import datetime
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.stock.repositories import StockRepository
from src.database.models import Stock, StockTransaction
from src.errors.stock import StockException


stock_repository = StockRepository()

class AdjustForPR:
    async def adjust_stock_for_purchase_return(self, session: AsyncSession, warehouse_id: str, product_variant_id: str,
                                               quantity_to_return: int, unit_cost: int, reference_id: str, 
                                               reference_type: str = "purchase_return", reason: str = None, 
                                               performed_by: Optional[str] = None):
        stock = await self.get_or_create_stock(
            session=session,
            warehouse_id=warehouse_id,
            product_variant_id=product_variant_id
        )
        
        if stock.quantity < quantity_to_return:
            StockException.insufficient_to_complete_return_purchase(stock.quantity, quantity_to_return)
            
        if stock.available_quantity < quantity_to_return:
            StockException.insufficient_available_to_complete_pr(stock.available_quantity, quantity_to_return)
            
        previous_quantity = stock.quantity
        previous_available = stock.available_quantity
        
        stock.quantity -= quantity_to_return
        stock.available_quantity -= quantity_to_return
        stock.last_outbound_date = datetime.now()
        stock.updated_at = datetime.now()
        
        stock.status = self.calculate_stock_status(stock)
        
        session.add(stock)
        await session.flush()
        
        await self.create_stock_transaction(
            session=session,
            warehouse_id=warehouse_id,
            stock_id=str(stock.id),
            product_variant_id=product_variant_id,
            transaction_type="outbound",            # hoàn trả = xuất kho
            quantity=-quantity_to_return,           # NEGATIVE for outbound
            previous_quantity=previous_quantity,
            new_quantity=stock.quantity,
            unit_cost=unit_cost,
            total_cost=unit_cost * quantity_to_return,
            reference_id=reference_id,
            reference_type=reference_type,
            reason=reason or "Hoàn trả hàng cho nhà cung cấp",
            performed_by=performed_by
        )

        return stock
    
    
    async def get_or_create_stock(self, session: AsyncSession, warehouse_id: str, product_variant_id: str):
        conditions = [
            Stock.warehouse_id == warehouse_id,
            Stock.product_variant_id == product_variant_id
        ]
        
        stock = await stock_repository.get_stock(session=session, where_conditions=conditions)
        
        if stock:
            return stock
        
        new_stock = Stock(
            warehouse_id=warehouse_id,
            product_variant_id=product_variant_id,
            quantity=0,
            reserved_quantity=0,
            available_quantity=0,
            status="out_of_stock",
            created_at=datetime.now()
        )
        
        session.add(new_stock)
        await session.flush()
        
        return new_stock
    
    
    def calculate_stock_status(self, stock: Stock):
        if stock.quantity <= 0:
            return "out_of_stock"
        
        if stock.min_stock_level and stock.quantity <= stock.min_stock_level:
            return "low_stock"
        
        if stock.max_stock_level and stock.quantity >= stock.max_stock_level:
            return "overstock"
        
        return "available"
    
    
    async def create_stock_transaction(self, session: AsyncSession, warehouse_id: str, stock_id: str, product_variant_id: str,
                                       transaction_type: str, quantity: int, previous_quantity: int, new_quantity: int, 
                                       unit_cost: Optional[int], total_cost: Optional[int], reference_id: str, 
                                       reference_type: str, reason: Optional[str], performed_by: Optional[str]):
        transaction = StockTransaction(
            warehouse_id=warehouse_id,
            stock_id=stock_id,
            product_variant_id=product_variant_id,
            transaction_type=transaction_type,
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            reference_id=reference_id,
            reference_type=reference_type,
            reason=reason,
            performed_by=performed_by,
            created_at=datetime.now()
        )
        
        session.add(transaction)
        await session.flush()
        
        return transaction