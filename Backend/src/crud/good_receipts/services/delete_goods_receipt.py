from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.good_receipts.services.utils_service import UtilsGRService
from src.database.models import GoodsReceipt
from src.errors.goods_receipt import GoodsReceiptException


utils_gr_service = UtilsGRService()
goods_receipt_repository = GoodsReceiptRepository()

class DeleteGoodsReceiptService:
    async def delete_goods_receipt(self, session: AsyncSession, goods_receipt_id: str):
        gr = await utils_gr_service.validate_draft_status(session, goods_receipt_id)
        
        condition_child = [GoodsReceipt.parent_receipt_id == goods_receipt_id]
        has_child_receipts, _ = await goods_receipt_repository.get_all_goods_receipt(session=session, where_conditions=condition_child)
        
        if len(has_child_receipts) > 0:
            GoodsReceiptException.cant_delete_receipt_have_child()
        
        if gr.purchase_returns and len(gr.purchase_returns) > 0:
            GoodsReceiptException.cant_delete_receipt_have_returns()
        
        success = await goods_receipt_repository.delete_goods_receipt(goods_receipt_id=goods_receipt_id, session=session)
        if not success:
            GoodsReceiptException.error_while_delete_pr()




