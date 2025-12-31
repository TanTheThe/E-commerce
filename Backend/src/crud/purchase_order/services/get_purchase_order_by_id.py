from typing import Any, Dict, List
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.user.repositories import UserRepository
from src.database.models import Product_Variant, PurchaseOrderDetail, PurchaseOrder, User
from src.errors.purchase_order import PurchaseOrderException

purchase_order_repository = PurchaseOrderRepository()
user_repository = UserRepository()


class GetPurchaseOrderByIDService:
    async def get_purchase_order(self, po_id: str, session: AsyncSession):
        condition_po = [PurchaseOrder.id == po_id]

        options = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
            selectinload(PurchaseOrder.po_details).selectinload(
                PurchaseOrderDetail.product_variant
            ).selectinload(Product_Variant.product),
            selectinload(PurchaseOrder.po_details).selectinload(
                PurchaseOrderDetail.product_variant
            ).selectinload(Product_Variant.color)
        ]

        po = await purchase_order_repository.get_purchase_order(
            session=session,
            where_conditions=condition_po,
            options=options
        )
        if not po:
            PurchaseOrderException.po_not_found()

        user_ids = []
        if po.created_by:
            user_ids.append(po.created_by)
        if po.approved_by and po.approved_by != po.created_by:
            user_ids.append(po.approved_by)

        users_dict = {}
        if user_ids:
            users_dict = await self.get_users_batch(session, user_ids)

        created_by_name = None
        if po.created_by and str(po.created_by) in users_dict:
            creator = users_dict[str(po.created_by)]
            created_by_name = f"{creator.first_name} {creator.last_name}".strip()

        approved_by_name = None
        if po.approved_by and str(po.approved_by) in users_dict:
            approver = users_dict[str(po.approved_by)]
            approved_by_name = f"{approver.first_name} {approver.last_name}".strip()

        items = self.build_po_items(po.po_details)

        return {
            "id": str(po.id),
            "po_number": po.po_number,
            "supplier_id": str(po.supplier_id) if po.supplier_id else None,
            "supplier_name": po.supplier.name if po.supplier else None,
            "supplier_code": po.supplier.code if po.supplier else None,
            "warehouse_id": str(po.warehouse_id) if po.warehouse_id else None,
            "warehouse_name": po.warehouse.name if po.warehouse else None,
            "warehouse_code": po.warehouse.code if po.warehouse else None,
            "status": po.status,
            "order_date": po.order_date.isoformat() if po.order_date else None,
            "expected_delivery_date": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None,
            "sub_total": po.sub_total,
            "discount_amount": po.discount_amount,
            "shipping_cost": po.shipping_cost,
            "total_amount": po.total_amount,
            "payment_status": po.payment_status,
            "paid_amount": po.paid_amount,
            "notes": po.notes,
            "created_by": str(po.created_by) if po.created_by else None,
            "created_by_name": created_by_name,
            "approved_by": str(po.approved_by) if po.approved_by else None,
            "approved_by_name": approved_by_name,
            "created_at": po.created_at.isoformat() if po.created_at else None,
            "approved_at": po.approved_at.isoformat() if po.approved_at else None,
            "sent_at": po.sent_at.isoformat() if po.sent_at else None,
            "confirmed_at": po.confirmed_at.isoformat() if po.confirmed_at else None,
            "completed_at": po.completed_at.isoformat() if po.completed_at else None,
            "updated_at": po.updated_at.isoformat() if po.updated_at else None,
            "cancelled_at": po.cancelled_at.isoformat() if po.cancelled_at else None,
            "cancellation_reason": po.cancellation_reason,
            "supplier_invoice_urls": po.supplier_invoice_urls,
            "items": items
        }

    async def get_users_batch(self, session: AsyncSession, user_ids: List[str]) -> Dict[str, Any]:
        condition = [User.id.in_(user_ids)]
        users = await user_repository.get_all_users(
            session=session,
            where_conditions=condition
        )

        return {str(user.id): user for user in users}

    def build_po_items(self, po_details: List[PurchaseOrderDetail]) -> List[Dict]:
        items = []

        for detail in po_details:
            if detail.product_snapshot:
                product_name = detail.product_snapshot.get("product_name")
                variant_sku = detail.product_snapshot.get("variant_sku")
                variant_size = detail.product_snapshot.get("variant_size")
                variant_color_name = detail.product_snapshot.get("variant_color_name")
                variant_image = detail.product_snapshot.get("variant_image")
            else:
                product_name = None
                variant_sku = None
                variant_size = None
                variant_color_name = None
                variant_image = None

                if detail.product_variant:
                    variant_sku = detail.product_variant.sku
                    variant_size = detail.product_variant.size
                    variant_image = detail.product_variant.image

                    if detail.product_variant.product:
                        product_name = detail.product_variant.product.name

                    if detail.product_variant.color_name:
                        variant_color_name = detail.product_variant.color_name
                    elif detail.product_variant.color:
                        variant_color_name = detail.product_variant.color.name

            product_id = None
            if detail.product_variant:
                product_id = str(detail.product_variant.product_id) if detail.product_variant.product_id else None

            items.append({
                "id": str(detail.id),
                "product_id": product_id,
                "product_variant_id": str(detail.product_variant_id) if detail.product_variant_id else None,
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
                "created_at": detail.created_at.isoformat() if detail.created_at else None,
            })

        return items


