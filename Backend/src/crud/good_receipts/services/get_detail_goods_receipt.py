from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.database.models import GoodsReceipt, GoodsReceiptDetail, PurchaseOrder
from src.errors.goods_receipt import GoodsReceiptException


goods_receipt_repository = GoodsReceiptRepository()


class GetDetailGoodsReceiptService:
    async def get_goods_receipt_by_id(self, session: AsyncSession, goods_receipt_id: str):
        condition = [GoodsReceipt.id == goods_receipt_id]

        options = [
            selectinload(GoodsReceipt.purchase_order).selectinload(
                PurchaseOrder.po_details),
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.receipt_details).selectinload(
                GoodsReceiptDetail.product_variant
            ),
            selectinload(GoodsReceipt.purchase_returns)
        ]

        gr = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=condition,
            options=options
        )

        if not gr:
            GoodsReceiptException.gr_not_found()

        details = []
        for detail in gr.receipt_details:
            details.append({
                "id": str(detail.id),
                "product_variant": {
                    "id": str(detail.product_variant_id),
                    "sku": detail.product_variant.sku if detail.product_variant else None,
                    "name": detail.product_variant.name if detail.product_variant else None
                },
                "po_detail_id": str(detail.po_detail_id) if detail.po_detail_id else None,
                "ordered_quantity": detail.ordered_quantity,
                "received_quantity": detail.received_quantity,
                "accepted_quantity": detail.accepted_quantity,
                "rejected_quantity": detail.rejected_quantity,
                "unit_cost": detail.unit_cost,
                "total_cost": detail.total_cost,
                "quality_status": detail.quality_status,
                "rejection_reason": detail.rejection_reason,
                "notes": detail.notes
            })

        returns = []
        if gr.purchase_returns:
            for pr in gr.purchase_returns:
                returns.append({
                    "id": str(pr.id),
                    "return_number": pr.return_number,
                    "status": pr.status,
                    "total_return_amount": pr.total_return_amount,
                    "created_at": pr.created_at.isoformat()
                })

        return {
            "id": str(gr.id),
            "receipt_number": gr.receipt_number,
            "purchase_order": {
                "id": str(gr.purchase_order_id),
                "po_number": gr.purchase_order.po_number if gr.purchase_order else None,
                "status": gr.purchase_order.status if gr.purchase_order else None
            } if gr.purchase_order_id else None,
            "supplier": {
                "id": str(gr.supplier_id),
                "name": gr.supplier.name if gr.supplier else None,
                "code": gr.supplier.code if gr.supplier else None,
                "email": gr.supplier.email if gr.supplier else None,
                "phone": gr.supplier.phone if gr.supplier else None
            } if gr.supplier_id else None,
            "warehouse": {
                "id": str(gr.warehouse_id),
                "name": gr.warehouse.name if gr.warehouse else None,
                "code": gr.warehouse.code if gr.warehouse else None,
                "address": gr.warehouse.address if gr.warehouse else None
            } if gr.warehouse_id else None,
            "receipt_date": gr.receipt_date.isoformat() if gr.receipt_date else None,
            "status": gr.status,
            "parent_receipt_id": str(gr.parent_receipt_id) if gr.parent_receipt_id else None,
            "shipping_cost": gr.shipping_cost,
            "other_costs": gr.other_costs,
            "total_amount": gr.total_amount,
            "notes": gr.notes,
            "receipt_details": details,
            "purchase_returns": returns,
            "created_by": str(gr.created_by) if gr.created_by else None,
            "approved_by": str(gr.approved_by) if gr.approved_by else None,
            "created_at": gr.created_at.isoformat(),
            "approved_at": gr.approved_at.isoformat() if gr.approved_at else None,
            "completed_at": gr.completed_at.isoformat() if gr.completed_at else None,
            "updated_at": gr.updated_at.isoformat() if gr.updated_at else None
        }
