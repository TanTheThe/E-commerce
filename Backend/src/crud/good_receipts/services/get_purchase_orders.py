from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.user.repositories import UserRepository
from src.database.models import PurchaseOrder


purchase_order_repository = PurchaseOrderRepository()
user_repository = UserRepository()

class GetPurchaseOrdersService:
    async def get_purchase_orders(self, session: AsyncSession,
                                  status: Optional[str] = None,
                                  supplier_id: Optional[str] = None,
                                  warehouse_id: Optional[str] = None,
                                  payment_status: Optional[str] = None,
                                  from_date: Optional[datetime] = None,
                                  to_date: Optional[datetime] = None,
                                  skip: int = 0, limit: int = 10):
        conditions = []

        if status:
            conditions.append(PurchaseOrder.status == status)

        if supplier_id:
            conditions.append(PurchaseOrder.supplier_id == supplier_id)

        if warehouse_id:
            conditions.append(PurchaseOrder.warehouse_id == warehouse_id)

        if payment_status:
            conditions.append(PurchaseOrder.payment_status == payment_status)

        if from_date:
            conditions.append(PurchaseOrder.order_date >= from_date)

        if to_date:
            conditions.append(PurchaseOrder.order_date <= to_date)

        options = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse)
        ]

        order_by = desc(PurchaseOrder.created_at)

        pos, total = await purchase_order_repository.get_all_purchase_orders(session=session, where_conditions=conditions,
                                                                       order_by=order_by, skip=skip, limit=limit, options=options)

        items = []
        for po in pos:
            items.append(
                {
                    "id": str(po.id),
                    "po_number": po.po_number,
                    "supplier_name": po.supplier.name if po.supplier else None,
                    "warehouse_name": po.warehouse.name if po.warehouse else None,
                    "status": po.status,
                    "order_date": str(po.order_date),
                    "expected_delivery_date": str(po.expected_delivery_date),
                    "total_amount": po.total_amount,
                    "payment_status": po.payment_status,
                    "created_at": str(po.created_at),
                    "supplier_invoice_urls": bool(po.supplier_invoice_urls),
                }
            )

        return {
            "data": items,
            "total": total,
        }



