from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import PurchaseOrder
from src.errors.purchase_order import PurchaseOrderException
from src.schemas.purchase_order import ApprovePurchaseOrderRequest

supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
purchase_order_repository = PurchaseOrderRepository()


class ApprovePurchaseOrderService:
    async def approve_purchase_order(self, session: AsyncSession, po_id: str, approved_by: str,
                                     request: Optional[ApprovePurchaseOrderRequest] = None):
        condition_po = [PurchaseOrder.id == po_id]

        options = [selectinload(PurchaseOrder.po_details)]

        po = await purchase_order_repository.get_purchase_order(
            session=session,
            where_conditions=condition_po,
            options=options
        )

        if not po:
            PurchaseOrderException.po_not_found()

        if po.status != "draft":
            PurchaseOrderException.only_sent_when_approved()

        if not po.po_details or len(po.po_details) == 0:
            PurchaseOrderException.cant_approve_po_with_no_details()

        now = datetime.now()

        update_data = {
            "status": "sent",
            "approved_by": approved_by,
            "approved_at": now,
            "sent_at": now,
            "updated_at": now
        }

        if request and request.notes:
            existing_notes = po.notes or ""
            approval_note = f"[Duyệt {now.strftime('%Y-%m-%d %H:%M')}] {request.notes}"

            if existing_notes:
                update_data["notes"] = f"{existing_notes}\n{approval_note}"
            else:
                update_data["notes"] = approval_note

        await purchase_order_repository.update_po_some_field(
            and_(*condition_po),
            update_data,
            session
        )

        await session.commit()

        return {
            "id": str(po.id),
            "po_number": po.po_number,
            "status": "sent",
            "approved_at": now.isoformat(),
            "sent_at": now.isoformat()
        }






