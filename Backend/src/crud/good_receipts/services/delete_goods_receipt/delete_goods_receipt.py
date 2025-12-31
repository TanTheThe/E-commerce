from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.services.delete_goods_receipt.delete_gr_validation import DeleteGRValidationService
import logging

logger = logging.getLogger(__name__)

validation_service = DeleteGRValidationService()


class DeleteGoodsReceiptService:
    async def delete_goods_receipt(self, goods_receipt_id: str, session: AsyncSession):
        try:
            gr = await validation_service.validate_gr_for_deletion(
                goods_receipt_id,
                session
            )

            validation_service.validate_gr_status(gr)

            await validation_service.validate_no_child_receipts(goods_receipt_id, session)

            validation_service.validate_no_purchase_returns(gr)

            await validation_service.validate_po_status(gr, session)

            validation_service.validate_not_referenced_by_stock(gr)

            deleted_details_count = await self.delete_receipt_details(gr, session)

            await session.delete(gr)

            await session.commit()

            return {
                "deleted_receipt": {
                    "id": str(gr.id),
                    "receipt_number": gr.receipt_number,
                    "status": gr.status
                },
                "cascade_deleted": {
                    "receipt_details_count": deleted_details_count
                },
                "deleted_at": datetime.now().isoformat()
            }

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to delete goods receipt: {str(e)}")
            raise


    async def delete_receipt_details(self, gr, session: AsyncSession):
        deleted_count = 0

        for detail in gr.receipt_details[:]:
            await session.delete(detail)
            deleted_count += 1

        gr.receipt_details.clear()

        return deleted_count