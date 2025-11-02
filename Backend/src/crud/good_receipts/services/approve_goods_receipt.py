from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.good_receipts.services.utils_service import UtilsGRService
from src.crud.stock.services.update_stock_completed_receipts import StockUpdateCompletedReceiptService
from src.database.models import GoodsReceipt, PurchaseOrder
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_order import PurchaseOrderException


goods_receipt_repository = GoodsReceiptRepository()
stock_update_completed_receipts_service = StockUpdateCompletedReceiptService()
utils_GR_service = UtilsGRService()


class ApproveGoodsReceiptService:
    async def approve_goods_receipt(self, session: AsyncSession, goods_receipt_id: str, approved_by: str):
        gr, po, all_related_grs = await self.validate_and_get_data(
            session, goods_receipt_id
        )

        variant_summary = utils_GR_service.calculate_total_accepted_quantity(all_related_grs, gr)
        po_details_map = {str(detail.id): detail for detail in po.po_details}
        status_info = utils_GR_service.determine_status_based_on_po(variant_summary, po_details_map)

        gr.status = status_info['gr_status']
        gr.approved_by = approved_by
        gr.approved_at = datetime.now()

        if status_info['all_completed']:
            result = await self.handle_completed_case(
                gr=gr,
                po=po,
                all_related_grs=all_related_grs,
                approved_by=approved_by,
                session=session,
                status_info=status_info
            )
        else:
            result = await self.handle_partial_case(
                gr=gr,
                po=po,
                po_details_map=po_details_map,
                session=session,
                status_info=status_info
            )

        await session.commit()
        await session.refresh(gr)

        return result

    async def validate_and_get_data(self, session: AsyncSession, goods_receipt_id: str):
        conditions = [
            GoodsReceipt.id == goods_receipt_id
        ]

        options = [
            selectinload(GoodsReceipt.purchase_order).selectinload(
                PurchaseOrder.po_details),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.receipt_details)
        ]

        gr = await goods_receipt_repository.get_goods_receipt(session=session, where_conditions=conditions,
                                                              options=options)

        if not gr:
            GoodsReceiptException.gr_not_found()

        if gr.status != "pending":
            GoodsReceiptException.only_approved_when_pending()

        po = gr.purchase_order
        if not po:
            PurchaseOrderException.po_not_found()

        all_related_grs = await utils_GR_service.get_all_related_receipts(str(po.id), session)

        return gr, po, all_related_grs

    async def handle_completed_case(self, gr: GoodsReceipt, po: PurchaseOrder, all_related_grs: list,
                                    approved_by: str, session: AsyncSession, status_info: dict):
        gr.completed_at = datetime.now()

        await self.mark_all_receipts_completed(all_related_grs, session)

        stock_updates = await stock_update_completed_receipts_service.update_stock_for_completed_receipts(
            all_related_grs=all_related_grs,
            warehouse_id=str(gr.warehouse_id),
            approved_by=approved_by,
            session=session
        )

        po.status = "completed"
        po.updated_at = datetime.now()

        return {
            "message": "Duyệt phiếu thành công. Đơn hàng đã nhận đủ hàng, tất cả phiếu đã hoàn tất",
            "data": {
                "id": str(gr.id),
                "receipt_number": gr.receipt_number,
                "old_status": "pending",
                "new_status": gr.status,
                "approved_by": str(gr.approved_by),
                "approved_at": gr.approved_at.isoformat(),
                "completed_at": gr.completed_at.isoformat() if gr.completed_at else None,
                "purchase_order": {
                    "id": str(po.id),
                    "po_number": po.po_number,
                    "status": po.status
                },
                "all_completed": True,
                "stock_updated": stock_updates,
                "comparison_details": status_info['comparison_details']
            }
        }

    async def handle_partial_case(self, gr: GoodsReceipt, po: PurchaseOrder, po_details_map: dict,
                                  session: AsyncSession, status_info: dict):
        await self.update_purchase_order_received_quantity(po, po_details_map, gr)

        po.status = "partial_received"
        po.updated_at = datetime.now()

        return {
            "message": "Duyệt phiếu thành công. Phiếu có hàng bị lỗi, cần tạo phiếu hoàn trả",
            "data": {
                "id": str(gr.id),
                "receipt_number": gr.receipt_number,
                "old_status": "pending",
                "new_status": gr.status,
                "approved_by": str(gr.approved_by),
                "approved_at": gr.approved_at.isoformat(),
                "completed_at": None,
                "purchase_order": {
                    "id": str(po.id),
                    "po_number": po.po_number,
                    "status": po.status
                },
                "all_completed": False,
                "stock_updated": [],
                "comparison_details": status_info['comparison_details'],
                "note": "Tồn kho chưa được cập nhật. Cần tạo phiếu hoàn trả cho hàng còn thiếu."
            }
        }

    async def mark_all_receipts_completed(self, all_related_grs: list, session: AsyncSession):
        for gr in all_related_grs:
            if gr.status in ['approved', 'has_issue']:
                gr.status = "completed"
                gr.completed_at = datetime.now()

    async def update_purchase_order_received_quantity(self, po: PurchaseOrder, po_details_map: dict,
                                                      gr: GoodsReceipt):
        for detail in gr.receipt_details:
            po_detail = po_details_map.get(str(detail.po_detail_id))
            if po_detail:
                if po_detail.received_quantity is None:
                    po_detail.received_quantity = 0
                po_detail.received_quantity += detail.accepted_quantity
