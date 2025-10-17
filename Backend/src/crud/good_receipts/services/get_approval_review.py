from sqlalchemy.orm import selectinload
from sqlmodel import or_
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.database.models import GoodsReceipt, PurchaseOrder
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_order import PurchaseOrderException

goods_receipt_repository = GoodsReceiptRepository()

class ApprovalPreviewService:
    async def get_approval_preview(self, goods_receipt_id: str, session: AsyncSession):
        condition_gr = [GoodsReceipt.id == goods_receipt_id]
        options_gr = [
            selectinload(GoodsReceipt.purchase_order).selectinload(PurchaseOrder.po_details),
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.receipt_details)
        ]

        gr = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=condition_gr,
            options=options_gr
        )

        if not gr:
            GoodsReceiptException.gr_not_found()

        if gr.status != "pending":
            GoodsReceiptException.only_preview_pending()

        po = gr.purchase_order
        if not po:
            PurchaseOrderException.po_not_found()

        all_related_grs = await self.get_all_related_receipts(gr, str(po.id), session)

        variant_summary = self.calculate_total_accepted_quantity(all_related_grs, gr)

        po_details_map = {str(detail.id): detail for detail in po.po_details}
        status_info = self.determine_status_based_on_po(variant_summary, po_details_map)

        preview_data = {
            "goods_receipt": {
                "id": str(gr.id),
                "receipt_number": gr.receipt_number,
                "current_status": gr.status,
                "predicted_status": status_info['gr_status'],
                "warehouse": {
                    "id": str(gr.warehouse_id),
                    "name": gr.warehouse.name if gr.warehouse else None
                }
            },
            "purchase_order": {
                "id": str(po.id),
                "po_number": po.po_number,
                "current_status": po.status,
                "predicted_status": "completed" if status_info['all_completed'] else "partial_received"
            },
            "summary": {
                "all_completed": status_info['all_completed'],
                "will_update_stock": status_info['all_completed'],
                "total_variants": len(variant_summary),
                "message": self.generate_preview_message(status_info['all_completed'])
            },
            "variant_details": status_info['comparison_details'],
        }

        return preview_data


    async def get_all_related_receipts(self, current_gr: GoodsReceipt, po_id: str, session: AsyncSession):
        if not current_gr.parent_receipt_id:
            condition = [
                GoodsReceipt.purchase_order_id == po_id,
                or_(
                    GoodsReceipt.id == current_gr.id,
                    GoodsReceipt.parent_receipt_id == current_gr.id
                )
            ]
        else:
            parent_id = current_gr.parent_receipt_id
            condition = [
                GoodsReceipt.purchase_order_id == po_id,
                or_(
                    GoodsReceipt.id == parent_id,
                    GoodsReceipt.parent_receipt_id == parent_id
                )
            ]

        options = [selectinload(GoodsReceipt.receipt_details)]

        grs = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=condition,
            options=options
        )
        return grs


    def calculate_total_accepted_quantity(self, all_related_grs: list, current_gr: GoodsReceipt) -> dict:
        variant_summary = {}

        for related_gr in all_related_grs:
            for detail in related_gr.receipt_details:
                variant_id = str(detail.product_variant_id)
                po_detail_id = str(detail.po_detail_id)

                if variant_id not in variant_summary:
                    variant_summary[variant_id] = {
                        'po_detail_id': po_detail_id,
                        'total_accepted': 0
                    }

                if related_gr.id == current_gr.id:
                    variant_summary[variant_id]['total_accepted'] += detail.accepted_quantity
                elif related_gr.status in ['approved', 'completed', 'has_issue']:
                    variant_summary[variant_id]['total_accepted'] += detail.accepted_quantity

        return variant_summary


    def determine_status_based_on_po(self, variant_summary: dict, po_details_map: dict) -> dict:
        all_completed = True
        comparison_details = []

        for variant_id, summary in variant_summary.items():
            po_detail_id = summary['po_detail_id']
            po_detail = po_details_map.get(po_detail_id)

            if not po_detail:
                continue

            ordered_qty = po_detail.quantity
            total_accepted_qty = summary['total_accepted']
            is_complete = total_accepted_qty >= ordered_qty

            comparison_details.append({
                'variant_id': variant_id,
                'po_detail_id': po_detail_id,
                'ordered': ordered_qty,
                'total_accepted': total_accepted_qty,
                'remaining': max(0, ordered_qty - total_accepted_qty),
                'is_complete': is_complete,
                'percentage': round((total_accepted_qty / ordered_qty * 100), 2) if ordered_qty > 0 else 0
            })

            if not is_complete:
                all_completed = False

        gr_status = "completed" if all_completed else "has_issue"

        return {
            'gr_status': gr_status,
            'all_completed': all_completed,
            'comparison_details': comparison_details
        }


    def generate_preview_message(self, all_completed: bool) -> str:
        if all_completed:
            return "Nếu duyệt phiếu này, đơn hàng sẽ được hoàn tất và tồn kho sẽ được cập nhật"
        else:
            return "Nếu duyệt phiếu này, phiếu sẽ có trạng thái 'có vấn đề' và cần tạo phiếu hoàn trả"



