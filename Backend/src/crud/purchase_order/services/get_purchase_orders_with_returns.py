from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.user.repositories import UserRepository
from src.database.models import PurchaseOrder, PurchaseReturn

purchase_order_repository = PurchaseOrderRepository()
purchase_return_repository = PurchaseReturnRepository()
goods_receipt_repository = GoodsReceiptRepository()
user_repository = UserRepository()

class GetPurchaseOrdersWithReturnsService:
    async def get_purchase_orders_with_returns(self, session: AsyncSession, warehouse_id: str,
                                                status_po: Optional[str] = None, search: Optional[str] = None,
                                                skip: int = 0, limit: int = 12):
        conditions = []

        po_has_pr_subquery = select(PurchaseReturn.purchase_order_id).distinct().where(PurchaseReturn.warehouse_id == warehouse_id)

        conditions.append(PurchaseOrder.id.in_(po_has_pr_subquery))

        if status_po:
            conditions.append(PurchaseOrder.status == status_po)

        if search:
            conditions.append(PurchaseOrder.po_number.ilike(f"%{search}%"))

        options = [
            selectinload(PurchaseOrder.po_details)
        ]

        order_by = desc(PurchaseOrder.created_at)

        pos, total = await purchase_order_repository.get_all_purchase_orders(session=session, where_conditions=conditions,
                                                                       order_by=order_by, skip=skip, limit=limit, options=options)

        items = []
        for po in pos:
            total_ordered = sum(detail.quantity for detail in po.po_details) if po.po_details else 0

            _, pr_count = await purchase_return_repository.get_all_purchase_returns(
                session=session,
                where_conditions=[PurchaseReturn.purchase_order_id == po.id, PurchaseReturn.warehouse_id == warehouse_id])

            items.append({
                "id": str(po.id),
                "po_number": po.po_number,
                "status": po.status,
                "total_ordered": total_ordered,
                "total_gr_count": pr_count,
                "created_at": po.created_at.isoformat(),
                "updated_at": po.updated_at.isoformat() if po.updated_at else None
            })

        return {
            "data": items,
            "total": total
        }



