from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.database.models import GoodsReceipt, PurchaseOrder
from src.errors.goods_receipt import GoodsReceiptException

goods_receipt_repository = GoodsReceiptRepository()

class ApprovalPreviewDataLoaderService:
    async def load_goods_receipt_with_relations(self, goods_receipt_id: str, session: AsyncSession):
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
            raise GoodsReceiptException.gr_not_found()

        return gr


    async def load_all_root_receipts(self, po_id: str, session: AsyncSession):
        condition = [
            GoodsReceipt.purchase_order_id == po_id,
            GoodsReceipt.parent_receipt_id.is_(None)
        ]
        options = [selectinload(GoodsReceipt.receipt_details)]

        root_grs, _ = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=condition,
            options=options
        )

        return root_grs


    async def load_children_receipts_batch(self, parent_ids: List[str], po_id: str, session: AsyncSession) -> List:
        if not parent_ids:
            return []

        condition = [
            GoodsReceipt.purchase_order_id == po_id,
            GoodsReceipt.parent_receipt_id.in_(parent_ids)
        ]
        options = [selectinload(GoodsReceipt.receipt_details)]

        children, _ = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=condition,
            options=options
        )

        return children