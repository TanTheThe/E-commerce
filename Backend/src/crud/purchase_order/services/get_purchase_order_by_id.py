from sqlalchemy.orm import selectinload
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.user.repositories import UserRepository
from src.database.models import Product_Variant, PurchaseOrderDetail, PurchaseOrder, User
from src.errors.purchase_order import PurchaseOrderException


purchase_order_repository = PurchaseOrderRepository()
user_repository = UserRepository()

class GetPurchaseOrderByIDService:
    async def get_purchase_order(self, po_id: str, session: AsyncSession):
        condition_po = [
            PurchaseOrder.id == po_id,
        ]
        options = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.product),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.color)
        ]
        po = await purchase_order_repository.get_purchase_order(session=session, where_conditions=condition_po, options=options)
        if not po:
            PurchaseOrderException.po_not_found()

        created_by_name = None
        if po.created_by:
            condition_user = and_(User.id == po.created_by)
            creator = await user_repository.get_user(condition_user, session=session)
            if creator:
                created_by_name = f"{creator.first_name} {creator.last_name}"

        approved_by_name = None
        if po.approved_by:
            condition_user = and_(User.id == po.approved_by)
            approver = await user_repository.get_user(condition_user, session=session)
            if approver:
                approved_by_name = f"{approver.first_name} {approver.last_name}"

        items = []
        for detail in po.po_details:
            if detail.product_snapshot:
                product_name = detail.product_snapshot.get("product_name")
                variant_sku = detail.product_snapshot.get("variant_sku")
                variant_size = detail.product_snapshot.get("variant_size")
                variant_color_name = detail.product_snapshot.get("variant_color_name")
                variant_image = detail.product_snapshot.get("variant_image")
            else:
                product_name = detail.product_variant.product.name if detail.product_variant and detail.product_variant.product else None
                variant_sku = detail.product_variant.sku if detail.product_variant else None
                variant_size = detail.product_variant.size if detail.product_variant else None

                variant_color_name = None
                variant_image = None
                if detail.product_variant:
                    if detail.product_variant.color_name:
                        variant_color_name = detail.product_variant.color_name
                    elif detail.product_variant.color:
                        variant_color_name = detail.product_variant.color.name
                    variant_image = detail.product_variant.image

            items.append(
                {
                    "id": str(detail.id),
                    "product_id": str(detail.product_variant.product_id),
                    "product_variant_id": str(detail.product_variant_id),
                    "product_name": product_name,
                    "variant_sku": variant_sku,
                    "variant_size": variant_size,
                    "variant_color_name": variant_color_name,
                    "variant_image": variant_image,
                    "quantity": detail.quantity,
                    "received_quantity": detail.received_quantity,
                    "unit_cost": detail.unit_cost,
                    "total_cost": detail.total_cost,
                    "product_snapshot": detail.product_snapshot,
                    "notes": detail.notes,
                    "created_at": str(detail.created_at),
                }
            )

        return {
            "id": str(po.id),
            "po_number": po.po_number,
            "supplier_id": str(po.supplier_id),
            "supplier_name": po.supplier.name if po.supplier else None,
            "supplier_code": po.supplier.code if po.supplier else None,
            "warehouse_id": str(po.warehouse_id),
            "warehouse_name": po.warehouse.name if po.warehouse else None,
            "warehouse_code": po.warehouse.code if po.warehouse else None,
            "status": po.status,
            "order_date": str(po.order_date),
            "expected_delivery_date": str(po.expected_delivery_date),
            "sub_total": str(po.sub_total),
            "discount_amount": po.discount_amount,
            "shipping_cost": po.shipping_cost,
            "total_amount": po.total_amount,
            "payment_status": po.payment_status,
            "paid_amount": po.paid_amount,
            "notes": po.notes,
            "created_by": str(po.created_by),
            "created_by_name": created_by_name,
            "approved_by": str(po.approved_by),
            "approved_by_name": approved_by_name,
            "created_at": str(po.created_at),
            "approved_at": str(po.approved_at),
            "sent_at": str(po.sent_at),
            "confirmed_at": str(po.confirmed_at),
            "completed_at": str(po.completed_at),
            "updated_at": str(po.updated_at),
            "cancelled_at": str(po.cancelled_at),
            "cancellation_reason": po.cancellation_reason,
            "supplier_invoice_urls": po.supplier_invoice_urls,
            "items": items
        }



