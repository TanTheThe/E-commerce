from sqlalchemy import func
from sqlalchemy.orm import selectinload, aliased
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.database.models import PurchaseReturn, PurchaseReturnDetail, GoodsReceiptDetail, Product_Variant
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_return import PurchaseReturnException

purchase_return_repository = PurchaseReturnRepository()
goods_receipt_repository = GoodsReceiptRepository()

class UtilsPRService:
    async def validate_and_get_pr(self, session: AsyncSession, purchase_return_id: str):
        condition = [PurchaseReturn.id == purchase_return_id]
        options = [
            selectinload(PurchaseReturn.purchase_order),
            selectinload(PurchaseReturn.goods_receipt),
            selectinload(PurchaseReturn.supplier),
            selectinload(PurchaseReturn.warehouse),
            selectinload(PurchaseReturn.return_details).selectinload(PurchaseReturnDetail.product_variant).selectinload(
                Product_Variant.product)
        ]

        pr = await purchase_return_repository.get_purchase_return(
            session=session,
            where_conditions=condition,
            options=options
        )

        if not pr:
            PurchaseReturnException.pr_not_found()

        return pr


    async def validate_draft_status(self, session: AsyncSession, purchase_return_id: str):
        condition = [PurchaseReturn.id == purchase_return_id]
        options = [selectinload(PurchaseReturn.return_details)]

        pr = await purchase_return_repository.get_purchase_return(
            session=session,
            where_conditions=condition,
            options=options
        )

        if not pr:
            PurchaseReturnException.pr_not_found()

        if pr.status != "draft":
            PurchaseReturnException.only_update_when_draft()

        return pr

    async def get_already_returned_quantity(self, session: AsyncSession, gr_detail_id: str, include_draft: bool = False):
        if include_draft:
            status_filter = PurchaseReturn.status != 'cancelled'
        else:
            status_filter = PurchaseReturn.status.in_(['approved', 'completed'])

        query = select(func.coalesce(func.sum(PurchaseReturnDetail.return_quantity), 0)) \
            .select_from(PurchaseReturnDetail) \
            .join(PurchaseReturn, PurchaseReturnDetail.purchase_return_id == PurchaseReturn.id) \
            .where(
            PurchaseReturnDetail.goods_receipt_detail_id == gr_detail_id,
            status_filter
        )

        result = await session.execute(query)
        return result.scalar()

    async def sync_returned_quantity(self, session: AsyncSession, gr_detail_id: str):
        total_returned = await self.get_already_returned_quantity(
            session,
            gr_detail_id,
            include_draft=False
        )

        gr_detail = await goods_receipt_repository.get_goods_receipt_detail(
            session=session,
            where_conditions=[GoodsReceiptDetail.id == gr_detail_id]
        )

        if not gr_detail:
            GoodsReceiptException.gr_detail_not_found()

        if total_returned > gr_detail.rejected_quantity:
            GoodsReceiptException.total_returned_greater_than_accepted_quantity()

        if total_returned > gr_detail.accepted_quantity:
            GoodsReceiptException.total_returned_greater_than_accepted_quantity()

        gr_detail.returned_quantity = total_returned
        session.add(gr_detail)
        await session.flush()