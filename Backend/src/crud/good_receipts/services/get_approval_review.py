from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.good_receipts.services.utils_service import UtilsGRService
from src.database.models import GoodsReceipt, PurchaseOrder
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_order import PurchaseOrderException

goods_receipt_repository = GoodsReceiptRepository()
utils_gr_service = UtilsGRService()

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

        all_related_grs = await utils_gr_service.get_all_related_receipts(gr, str(po.id), session)

        variant_summary = utils_gr_service.calculate_total_accepted_quantity(all_related_grs, gr)

        po_details_map = {str(detail.id): detail for detail in po.po_details}
        status_info = utils_gr_service.determine_status_based_on_po(variant_summary, po_details_map)

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

    def generate_preview_message(self, all_completed: bool):
        if all_completed:
            return "Nếu duyệt phiếu này, đơn hàng sẽ được hoàn tất và tồn kho sẽ được cập nhật"
        else:
            return "Nếu duyệt phiếu này, phiếu sẽ có trạng thái 'có vấn đề' và cần tạo phiếu hoàn trả"



