from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.user.repositories import UserRepository
from src.database.models import GoodsReceipt, GoodsReceiptDetail, Product_Variant, User
from src.errors.goods_receipt import GoodsReceiptException


goods_receipt_repository = GoodsReceiptRepository()
user_repository = UserRepository()


class GetDetailGoodsReceiptService:
    async def get_goods_receipt(self, gr_id: str, session: AsyncSession):
        condition_gr = [GoodsReceipt.id == gr_id]

        options = [
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.purchase_order),
            selectinload(GoodsReceipt.receipt_details).selectinload(
                GoodsReceiptDetail.product_variant
            ).selectinload(Product_Variant.product),
            selectinload(GoodsReceipt.receipt_details).selectinload(
                GoodsReceiptDetail.product_variant
            ).selectinload(Product_Variant.color),
            selectinload(GoodsReceipt.receipt_details).selectinload(
                GoodsReceiptDetail.po_detail
            )
        ]

        gr = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=condition_gr,
            options=options
        )

        if not gr:
            GoodsReceiptException.gr_not_found()

        receipt_number_parent = None
        if gr.parent_receipt_id:
            parent_receipt = await goods_receipt_repository.get_goods_receipt(
                session=session,
                where_conditions=[GoodsReceipt.id == gr.parent_receipt_id]
            )
            if parent_receipt:
                receipt_number_parent = parent_receipt.receipt_number

        user_ids = [
            user_id for user_id in [gr.received_by, gr.inspected_by, gr.approved_by]
            if user_id is not None
        ]

        user_map = {}
        if user_ids:
            users, _ = await user_repository.get_all_users(
                where_conditions=[User.id.in_(user_ids)],
                session=session
            )
            user_map = {
                str(user.id): f"{user.first_name} {user.last_name}"
                for user in users
            }

        received_by_name = user_map.get(str(gr.received_by)) if gr.received_by else None
        inspected_by_name = user_map.get(str(gr.inspected_by)) if gr.inspected_by else None
        approved_by_name = user_map.get(str(gr.approved_by)) if gr.approved_by else None

        items = []
        for detail in gr.receipt_details:
            if detail.product_snapshot:
                product_name = detail.product_snapshot.get("product_name")
                variant_sku = detail.product_snapshot.get("variant_sku")
                variant_size = detail.product_snapshot.get("variant_size")
                variant_color_name = detail.product_snapshot.get("variant_color_name")
                variant_image = detail.product_snapshot.get("variant_image")
            else:
                product_variant = detail.product_variant
                product = product_variant.product if product_variant else None

                product_name = product.name if product else None
                variant_sku = product_variant.sku if product_variant else None
                variant_size = product_variant.size if product_variant else None
                variant_image = product_variant.image if product_variant else None

                variant_color_name = None
                if product_variant:
                    variant_color_name = (
                            product_variant.color_name or
                            (product_variant.color.name if product_variant.color else None)
                    )

            items.append({
                "id": str(detail.id),
                "product_id": str(detail.product_variant.product_id) if detail.product_variant else None,
                "product_variant_id": str(detail.product_variant_id),
                "po_detail_id": str(detail.po_detail_id) if detail.po_detail_id else None,
                "product_name": product_name,
                "variant_sku": variant_sku,
                "variant_size": variant_size,
                "variant_color_name": variant_color_name,
                "variant_image": variant_image,
                "ordered_quantity": detail.ordered_quantity,
                "received_quantity": detail.received_quantity,
                "accepted_quantity": detail.accepted_quantity,
                "rejected_quantity": detail.rejected_quantity,
                "returned_quantity": detail.returned_quantity,
                "unit_cost": float(detail.unit_cost) if detail.unit_cost else None,
                "total_cost": float(detail.total_cost) if detail.total_cost else None,
                "rejection_reason": detail.rejection_reason,
                "product_snapshot": detail.product_snapshot,
                "notes": detail.notes,
                "created_at": detail.created_at.isoformat() if detail.created_at else None,
            })

        return {
            "id": str(gr.id),
            "receipt_number": gr.receipt_number,
            "purchase_order_id": str(gr.purchase_order_id),
            "purchase_order_number": gr.purchase_order.po_number if gr.purchase_order else None,
            "warehouse_id": str(gr.warehouse_id),
            "warehouse_name": gr.warehouse.name if gr.warehouse else None,
            "warehouse_code": gr.warehouse.code if gr.warehouse else None,
            "supplier_id": str(gr.supplier_id),
            "supplier_name": gr.supplier.name if gr.supplier else None,
            "supplier_code": gr.supplier.code if gr.supplier else None,
            "parent_receipt_id": str(gr.parent_receipt_id) if gr.parent_receipt_id else None,
            "receipt_number_parent": receipt_number_parent,
            "status": gr.status,
            "receipt_date": str(gr.receipt_date),
            "total_received_amount": gr.total_received_amount,
            "delivery_note_number": gr.delivery_note_number,
            "received_by": str(gr.received_by) if gr.received_by else None,
            "received_by_name": received_by_name,
            "inspected_by": str(gr.inspected_by) if gr.inspected_by else None,
            "inspected_by_name": inspected_by_name,
            "approved_by": str(gr.approved_by) if gr.approved_by else None,
            "approved_by_name": approved_by_name,
            "has_discrepancy": gr.has_discrepancy,
            "discrepancy_notes": gr.discrepancy_notes,
            "notes": gr.notes,
            "created_at": str(gr.created_at),
            "received_at": str(gr.received_at),
            "inspected_at": str(gr.inspected_at) if gr.inspected_at else None,
            "approved_at": str(gr.approved_at) if gr.approved_at else None,
            "completed_at": str(gr.completed_at) if gr.completed_at else None,
            "updated_at": str(gr.updated_at) if gr.updated_at else None,
            "items": items
        }
