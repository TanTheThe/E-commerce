from typing import Dict, Optional, List
from sqlalchemy.orm import selectinload
from sqlmodel import desc, select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.user.repositories import UserRepository
from src.database.models import PurchaseOrder, GoodsReceipt

purchase_order_repository = PurchaseOrderRepository()
goods_receipt_repository = GoodsReceiptRepository()
user_repository = UserRepository()


class GetPurchaseOrdersWithReceiptsService:
    async def get_purchase_orders_with_receipts(self, session: AsyncSession, warehouse_id: str,
                                                status_po: Optional[str] = None, search: Optional[str] = None,
                                                skip: int = 0, limit: int = 12):
        conditions = []

        po_has_gr_subquery = (
            select(GoodsReceipt.purchase_order_id)
            .distinct()
            .where(and_(GoodsReceipt.warehouse_id == warehouse_id))
        )

        conditions.append(PurchaseOrder.id.in_(po_has_gr_subquery))

        if status_po:
            conditions.append(PurchaseOrder.status == status_po)

        if search:
            search_term = search.strip()
            if search_term:
                conditions.append(PurchaseOrder.po_number.ilike(f"%{search_term}%"))

        options = [
            selectinload(PurchaseOrder.po_details)
        ]

        order_by = desc(PurchaseOrder.created_at)

        pos, total = await purchase_order_repository.get_all_purchase_orders(
            session=session,
            where_conditions=conditions,
            order_by=order_by,
            skip=skip,
            limit=limit,
            options=options
        )

        if not pos:
            return {"data": [], "total": 0}

        po_ids = [po.id for po in pos]
        gr_counts = await self.get_goods_receipt_counts_batch(session, po_ids, warehouse_id)

        items = []
        for po in pos:
            total_ordered = sum(detail.quantity for detail in po.po_details) if po.po_details else 0

            gr_count = gr_counts.get(str(po.id), 0)

            items.append({
                "id": str(po.id),
                "po_number": po.po_number,
                "status": po.status,
                "total_ordered": total_ordered,
                "total_gr_count": gr_count,
                "created_at": po.created_at.isoformat() if po.created_at else None,
                "updated_at": po.updated_at.isoformat() if po.updated_at else None
            })

        return {
            "data": items,
            "total": total
        }

    async def get_goods_receipt_counts_batch(self, session: AsyncSession, po_ids: List[str], warehouse_id: str) -> Dict[
        str, int]:
        conditions = [
            GoodsReceipt.purchase_order_id.in_(po_ids),
            GoodsReceipt.warehouse_id == warehouse_id
        ]

        group_by = [GoodsReceipt.purchase_order_id]

        rows, totals = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=conditions,
            group_by_columns=group_by
        )

        return {str(row.purchase_order_id): totals for row in rows}