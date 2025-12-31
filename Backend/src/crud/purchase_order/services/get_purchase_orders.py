from datetime import datetime
from typing import Optional, List
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
                                  status_list: Optional[List[str]] = None,
                                  supplier_id: Optional[str] = None,
                                  warehouse_id: Optional[str] = None,
                                  payment_status: Optional[str] = None,
                                  from_date: Optional[datetime] = None,
                                  to_date: Optional[datetime] = None,
                                  skip: int = 0, limit: int = 10):
        conditions = []

        if status_list:
            conditions.append(PurchaseOrder.status.in_(status_list))

        if supplier_id:
            conditions.append(PurchaseOrder.supplier_id == supplier_id)

        if warehouse_id:
            conditions.append(PurchaseOrder.warehouse_id == warehouse_id)

        if payment_status:
            conditions.append(PurchaseOrder.payment_status == payment_status)

        if from_date:
            conditions.append(PurchaseOrder.order_date >= from_date)

        if to_date:
            end_of_day = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            conditions.append(PurchaseOrder.order_date <= end_of_day)

        options = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse)
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

        items = [
            {
                "id": str(po.id),
                "po_number": po.po_number,
                "supplier_name": po.supplier.name if po.supplier else None,
                "warehouse_name": po.warehouse.name if po.warehouse else None,
                "status": po.status,
                "order_date": po.order_date.isoformat() if po.order_date else None,
                "expected_delivery_date": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None,
                "total_amount": po.total_amount,
                "payment_status": po.payment_status,
                "created_at": po.created_at.isoformat() if po.created_at else None,
                "has_supplier_invoice": bool(po.supplier_invoice_urls),
            }
            for po in pos
        ]

        return {
            "data": items,
            "total": total,
        }



