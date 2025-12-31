from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.database.models import GoodsReceipt
from src.errors.goods_receipt import GoodsReceiptException

goods_receipt_repository = GoodsReceiptRepository()

class DeleteGRValidationService:
    async def validate_gr_for_deletion(self, goods_receipt_id: str, session: AsyncSession):
        conditions = [GoodsReceipt.id == goods_receipt_id]
        options = [
            selectinload(GoodsReceipt.receipt_details),
            selectinload(GoodsReceipt.purchase_returns),
            selectinload(GoodsReceipt.purchase_order)
        ]

        gr = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=conditions,
            options=options
        )

        if not gr:
            raise GoodsReceiptException.gr_not_found()

        return gr


    def validate_gr_status(self, gr):
        if gr.status != "pending":
            raise GoodsReceiptException.can_only_delete_pending(gr.status)


    async def validate_no_child_receipts(self, goods_receipt_id: str, session: AsyncSession):
        condition_child = [GoodsReceipt.parent_receipt_id == goods_receipt_id]

        child_receipts, total = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=condition_child,
            limit=1
        )

        if total > 0:
            raise GoodsReceiptException.cant_delete_receipt_have_child()


    def validate_no_purchase_returns(self, gr):
        if gr.purchase_returns and len(gr.purchase_returns) > 0:
            raise GoodsReceiptException.cant_delete_receipt_have_returns()


    def validate_not_referenced_by_stock(self, gr):
        if gr.status in ['approved', 'completed']:
            raise GoodsReceiptException.cant_delete_stock_updated_gr()


    async def validate_po_status(self, gr, session: AsyncSession):
        if not gr.purchase_order:
            return

        po_status = gr.purchase_order.status

        if po_status == "completed":
            raise GoodsReceiptException.cant_delete_gr_of_completed_po()