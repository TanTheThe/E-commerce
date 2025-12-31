from datetime import datetime
from typing import Dict, List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.services.get_approval_preview.data_loader import ApprovalPreviewDataLoaderService
from src.crud.good_receipts.services.get_approval_preview.quantity_calculation import QuantityCalculationService
from src.crud.good_receipts.services.get_approval_preview.receipt_tree import ReceiptTreeService
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_order import PurchaseOrderException

data_loader_service = ApprovalPreviewDataLoaderService()
receipt_tree_service = ReceiptTreeService()
quantity_calculation_service = QuantityCalculationService()

class ApprovalPreviewService:
    async def get_approval_preview(self, goods_receipt_id: str, session: AsyncSession) -> Dict:
        gr = await data_loader_service.load_goods_receipt_with_relations(goods_receipt_id, session)

        if gr.status != "pending":
            GoodsReceiptException.only_preview_pending()

        if not gr.purchase_order:
            PurchaseOrderException.po_not_found()

        po = gr.purchase_order

        all_related_grs = await receipt_tree_service.get_all_related_receipts(gr, str(po.id), session)

        variant_summary = quantity_calculation_service.calculate_variant_summary(all_related_grs, gr)

        po_details_map = {str(detail.id): detail for detail in po.po_details}
        status_info = quantity_calculation_service.determine_completion_status(variant_summary, po_details_map)

        preview_data = self.build_preview_response(gr, po, status_info, variant_summary)

        return preview_data


    def generate_preview_message(self, all_completed: bool, total_variants: int) -> str:
        if all_completed:
            return (
                f"Nếu duyệt phiếu này, đơn hàng sẽ được hoàn tất. "
                f"Tồn kho sẽ được cập nhật cho {total_variants} sản phẩm."
            )
        else:
            return (
                f"Nếu duyệt phiếu này, phiếu sẽ có trạng thái 'Có vấn đề' do chưa nhận đủ hàng. "
                f"Bạn cần tạo phiếu nhập hàng bổ sung để hoàn tất đơn hàng."
            )


    def generate_status_summary(self, comparison_details: List[Dict]) -> Dict:
        total_items = len(comparison_details)
        completed_items = sum(1 for d in comparison_details if d['is_complete'])
        incomplete_items = total_items - completed_items

        total_ordered = sum(d['ordered'] for d in comparison_details)
        total_accepted = sum(d['total_accepted'] for d in comparison_details)
        total_remaining = sum(d['remaining'] for d in comparison_details)

        return {
            'total_items': total_items,
            'completed_items': completed_items,
            'incomplete_items': incomplete_items,
            'completion_percentage': round((completed_items / total_items * 100), 2) if total_items > 0 else 0,
            'total_ordered': total_ordered,
            'total_accepted': total_accepted,
            'total_remaining': total_remaining
        }


    def build_preview_response(self, gr, po, status_info: Dict, variant_summary: Dict) -> Dict:
        statistics = self.generate_status_summary(status_info['comparison_details'])

        return {
            "goods_receipt": {
                "id": str(gr.id),
                "receipt_number": gr.receipt_number,
                "receipt_date": gr.receipt_date.isoformat() if gr.receipt_date else None,
                "current_status": gr.status,
                "predicted_status": status_info['gr_status'],
                "warehouse": {
                    "id": str(gr.warehouse_id),
                    "name": gr.warehouse.name if gr.warehouse else None
                },
                "supplier": {
                    "id": str(gr.supplier_id),
                    "name": gr.supplier.name if gr.supplier else None
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
                "statistics": statistics,
                "message": self.generate_preview_message(
                    status_info['all_completed'],
                    len(variant_summary)
                )
            },
            "variant_details": status_info['comparison_details'],
            "generated_at": datetime.now().isoformat()
        }


