from datetime import datetime
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Product_Variant, PurchaseOrderDetail, PurchaseOrder
from src.errors.purchase_order import PurchaseOrderException

supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
purchase_order_repository = PurchaseOrderRepository()


class ConfirmPurchaseOrderService:
    async def confirm_purchase_order(self, po_id: str, session: AsyncSession):
        condition_po = [PurchaseOrder.id == po_id]
        options = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.product),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.color)
        ]

        po = await purchase_order_repository.get_purchase_order(
            session=session,
            where_conditions=condition_po,
            options=options
        )

        if not po:
            PurchaseOrderException.po_not_found()

        if po.status != "sent":
            PurchaseOrderException.only_sent_can_update()

        if not po.po_details or len(po.po_details) == 0:
            PurchaseOrderException.cant_confirm_po_without_details()

        if not po.supplier_invoice_urls or len(po.supplier_invoice_urls) == 0:
            PurchaseOrderException.cant_confirm_po_without_invoice()

        await purchase_order_repository.update_po_some_field(and_(*condition_po), {
            "status": "confirmed",
            "confirmed_at": datetime.now(),
            "updated_at": datetime.now()
        }, session)

        await session.commit()





