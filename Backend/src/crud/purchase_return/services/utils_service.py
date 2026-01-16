from typing import Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.database.models import PurchaseReturn, PurchaseReturnDetail, GoodsReceiptDetail, Product_Variant
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_return import PurchaseReturnException

purchase_return_repository = PurchaseReturnRepository()
goods_receipt_repository = GoodsReceiptRepository()

class UtilsPRService:
    async def validate_and_get_pr(self, session: AsyncSession, purchase_return_id: str, minimal: bool = False):
        condition = [PurchaseReturn.id == purchase_return_id]

        options = []
        if not minimal:
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

    async def get_already_returned_quantity(self, session: AsyncSession, gr_detail_id: str, include_draft: bool = False,
                                            exclude_detail_id: Optional[str] = None):
        if include_draft:
            status_filter = PurchaseReturn.status != 'cancelled'
        else:
            status_filter = PurchaseReturn.status.in_(['approved', 'sent', 'confirmed', 'completed'])

        conditions = [
            PurchaseReturnDetail.goods_receipt_detail_id == gr_detail_id,
            status_filter
        ]

        if exclude_detail_id:
            conditions.append(PurchaseReturnDetail.id != exclude_detail_id)

        query = (
            select(func.coalesce(func.sum(PurchaseReturnDetail.return_quantity), 0))
            .select_from(PurchaseReturnDetail)
            .join(PurchaseReturn, PurchaseReturnDetail.purchase_return_id == PurchaseReturn.id)
            .where(and_(*conditions))
        )

        result = await session.execute(query)
        return result.scalar()
        
        
    async def get_already_returned_quantities_batch(self, session: AsyncSession, gr_detail_ids: List[str],
                                                    include_draft: bool = False) -> Dict[str, int]:
        conditions = [PurchaseReturnDetail.goods_receipt_detail_id.in_(gr_detail_ids)]
    
        if not include_draft:
            conditions.append(PurchaseReturn.status != 'draft')
        
        select_columns = [
            PurchaseReturnDetail.goods_receipt_detail_id,
            func.sum(PurchaseReturnDetail.return_quantity).label('total_returned')
        ]
        
        joins = [
            (PurchaseReturn, {"type": "inner", "on": PurchaseReturn.id == PurchaseReturnDetail.purchase_return_id}),
        ]
        
        group_by = PurchaseReturnDetail.goods_receipt_detail_id
        
        rows, _ = purchase_return_repository.get_all_return_details(session=session, select_columns=select_columns, joins=joins,
                                                                    group_by_columns=group_by)
        
        return {str(row.goods_receipt_detail_id): row.total_returned for row in rows}
    
    
    async def batch_sync_returned_quantities(self, session: AsyncSession, gr_detail_ids: List[str]):
        returned_quantities = await self.get_already_returned_quantities_batch(
            session, 
            gr_detail_ids, 
            include_draft=False
        )
        
        gr_details = await goods_receipt_repository.get_all_goods_receipt_detail(
            session=session,
            where_conditions=[GoodsReceiptDetail.id.in_(gr_detail_ids)]
        )
        
        gr_details_map = {str(grd.id): grd for grd in gr_details}
        
        for gr_detail_id in gr_detail_ids:
            total_returned = returned_quantities.get(gr_detail_id, 0)
            gr_detail = gr_details_map.get(gr_detail_id)

            if not gr_detail:
                GoodsReceiptException.gr_detail_not_found()

            if total_returned > gr_detail.accepted_quantity:
                PurchaseReturnException.total_returned_exceeds_amount_received(total_returned, gr_detail.accepted_quantity)

            gr_detail.returned_quantity = total_returned
            session.add(gr_detail)
        
        await session.flush()

        
        
    
    
        
        
        