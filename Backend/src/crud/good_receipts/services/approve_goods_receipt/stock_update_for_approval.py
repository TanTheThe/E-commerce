from datetime import datetime
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.stock.repositories import StockRepository
from src.database.models import Stock

stock_repository = StockRepository()

class StockUpdateForApprovalService:
    async def update_stock_for_completed_receipts(self, all_related_grs: List, warehouse_id: str, approved_by: str,
                                                  session: AsyncSession):
        stock_updates = []
        now = datetime.now()

        variant_quantities = {}

        for gr in all_related_grs:
            if gr.status not in ['approved', 'has_issue']:
                continue

            for detail in gr.receipt_details:
                variant_id = str(detail.product_variant_id)

                if variant_id not in variant_quantities:
                    variant_quantities[variant_id] = {
                        'quantity': 0,
                        'sku': detail.product_snapshot.get('variant_sku') if detail.product_snapshot else None
                    }

                variant_quantities[variant_id]['quantity'] += detail.accepted_quantity

        for variant_id, info in variant_quantities.items():
            if info['quantity'] <= 0:
                continue

            stock = await self.get_or_create_stock(warehouse_id, variant_id, session)

            old_quantity = stock.quantity
            stock.quantity += info['quantity']
            stock.updated_at = now

            stock_updates.append({
                'variant_id': variant_id,
                'sku': info['sku'],
                'old_quantity': old_quantity,
                'added_quantity': info['quantity'],
                'new_quantity': stock.quantity
            })

        return stock_updates


    async def get_or_create_stock(self, warehouse_id: str, variant_id: str, session: AsyncSession):
        conditions = [
            Stock.warehouse_id == warehouse_id,
            Stock.product_variant_id == variant_id
        ]

        stock = await stock_repository.get_stock(
            session=session,
            where_conditions=conditions
        )

        if not stock:
            stock = Stock(
                warehouse_id=warehouse_id,
                product_variant_id=variant_id,
                quantity=0,
                created_at=datetime.now()
            )
            session.add(stock)

        return stock