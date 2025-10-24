from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Product_Variant, PurchaseOrderDetail, PurchaseOrder
from src.errors.purchase_order import PurchaseOrderException
from src.schemas.purchase_order import ApprovePurchaseOrderRequest

supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
purchase_order_repository = PurchaseOrderRepository()


class ApprovePurchaseOrderService:
    async def approve_purchase_order(self, session: AsyncSession, po_id: str, approved_by: str, request: Optional[ApprovePurchaseOrderRequest] = None):
        condition_po = [PurchaseOrder.id == po_id]
        options_po = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.product),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.color)
        ]

        po = await purchase_order_repository.get_purchase_order(session=session, where_conditions=condition_po, options=options_po)
        if not po:
            PurchaseOrderException.po_not_found()

        if po.status != "draft":
            PurchaseOrderException.only_sent_when_approved()

        if not po.po_details or len(po.po_details) == 0:
            PurchaseOrderException.cant_approve_po_with_no_details()

        po.status = "approved"
        po.approved_by = approved_by
        po.approved_at = datetime.now()
        po.updated_at = datetime.now()

        if request and request.notes:
            po.notes = f"{po.notes}\n[Duyệt] {request.notes}" if po.notes else f"[Duyệt] {request.notes}"

        updated_po = await purchase_order_repository.update_purchase_order(session, po)

        return {
            "id": str(updated_po.id),
        }






