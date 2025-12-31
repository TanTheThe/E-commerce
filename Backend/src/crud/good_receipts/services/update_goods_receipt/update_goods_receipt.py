from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.services.update_goods_receipt.receipt_detail_update import ReceiptDetailUpdateService
from src.crud.good_receipts.services.update_goods_receipt.update_gr_validation import UpdateGRValidationService
from src.schemas.goods_receipt import UpdateGoodsReceiptRequest
import logging


logger = logging.getLogger(__name__)

validation_service = UpdateGRValidationService()
detail_update_service = ReceiptDetailUpdateService()

class UpdateGoodsReceiptService:
    async def update_goods_receipt(self, goods_receipt_id: str, update_data: UpdateGoodsReceiptRequest, session: AsyncSession):
        try:
            gr = await validation_service.validate_gr_for_update(goods_receipt_id, session)

            deleted_count = 0

            if update_data.receipt_date is not None:
                gr.receipt_date = update_data.receipt_date

            if update_data.delivery_note_number is not None:
                gr.delivery_note_number = update_data.delivery_note_number

            if update_data.has_discrepancy is not None:
                gr.has_discrepancy = update_data.has_discrepancy

            if update_data.discrepancy_notes is not None:
                gr.discrepancy_notes = update_data.discrepancy_notes

            if update_data.notes is not None:
                gr.notes = update_data.notes

            if update_data.receipt_details is not None:
                variants_map, po_details_map = await validation_service.validate_receipt_details(
                    update_data.receipt_details,
                    gr,
                    session
                )

                deleted_count = await detail_update_service.update_receipt_details(
                    gr,
                    update_data.receipt_details,
                    variants_map,
                    po_details_map,
                    session
                )

            total_received_amount = sum(d.total_cost for d in gr.receipt_details)
            gr.total_received_amount = total_received_amount

            gr.updated_at = datetime.now()

            await session.commit()

            await session.refresh(gr)

            return {
                "id": str(gr.id),
                "receipt_number": gr.receipt_number,
                "receipt_date": gr.receipt_date.isoformat() if gr.receipt_date else None,
                "delivery_note_number": gr.delivery_note_number,
                "has_discrepancy": gr.has_discrepancy,
                "total_received_amount": gr.total_received_amount,
                "total_items": len(gr.receipt_details),
                "changes": {
                    "deleted_items_count": deleted_count
                },
                "updated_at": gr.updated_at.isoformat()
            }

        except Exception as e:
            await session.rollback()
            logger.error("Error update goods receipt: ", e)
            raise