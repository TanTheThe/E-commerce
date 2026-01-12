from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import asc, desc, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.database.models import GoodsReceipt, PurchaseReturn, PurchaseReturnDetail, Warehouse
from src.schemas.purchase_return import SortBy


purchase_return_repository = PurchaseReturnRepository()


class GetPurchaseReturnsService:
    async def get_purchase_returns(self, session: AsyncSession, warehouse_id: str, status_pr: Optional[str] = None,
                                   return_type: Optional[str] = None, purchase_order_id: Optional[str] = None,
                                   goods_receipt_id: Optional[str] = None, supplier_id: Optional[str] = None,
                                   from_date: Optional[datetime] = None, to_date: Optional[datetime] = None,
                                   search: Optional[str] = None, sort_by: Optional[SortBy] = None,
                                   skip: int = 0, limit: int = 10):
        
        conditions = [PurchaseReturn.warehouse_id == warehouse_id]

        if status_pr:
            conditions.append(PurchaseReturn.status == status_pr)

        if return_type:
            conditions.append(PurchaseReturn.return_type == return_type)

        if purchase_order_id:
            conditions.append(PurchaseReturn.purchase_order_id == purchase_order_id)

        if goods_receipt_id:
            conditions.append(PurchaseReturn.goods_receipt_id == goods_receipt_id)

        if supplier_id:
            conditions.append(PurchaseReturn.supplier_id == supplier_id)
            
        if from_date:
            from_date_start = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
            conditions.append(PurchaseReturn.return_date >= from_date_start)

        if to_date:
            to_date_end = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            conditions.append(PurchaseReturn.return_date <= to_date_end)

        if search:
            search_pattern = f"%{search.strip()}%"
            conditions.append(
                or_(
                    PurchaseReturn.return_number.ilike(search_pattern),
                    PurchaseReturn.delivery_note_number.ilike(search_pattern)
                )
            )

        options = [
            selectinload(PurchaseReturn.purchase_order),
            selectinload(PurchaseReturn.goods_receipt),
            selectinload(PurchaseReturn.supplier),
            selectinload(PurchaseReturn.warehouse),
            selectinload(PurchaseReturn.return_details).load_only(PurchaseReturnDetail.id)
        ]

        sort_by_result = desc(PurchaseReturn.return_date)
        
        if sort_by:
            if sort_by == SortBy.RETURN_DATE_ASC:
                sort_by_result = asc(PurchaseReturn.return_date)
            elif sort_by == SortBy.RETURN_DATE_DESC:
                sort_by_result = desc(PurchaseReturn.return_date)
            elif sort_by == SortBy.TOTAL_AMOUNT_ASC:
                sort_by_result = asc(PurchaseReturn.total_return_amount)
            elif sort_by == SortBy.TOTAL_AMOUNT_DESC:
                sort_by_result = desc(PurchaseReturn.total_return_amount)
            elif sort_by == SortBy.CREATED_AT_ASC:
                sort_by_result = asc(PurchaseReturn.created_at)
            elif sort_by == SortBy.CREATED_AT_DESC:
                sort_by_result = desc(PurchaseReturn.created_at)

        prs, total = await purchase_return_repository.get_all_purchase_returns(
            session=session, 
            where_conditions=conditions,
            order_by=sort_by_result, 
            skip=skip,
            limit=limit, 
            options=options
        )

        items = []
        for pr in prs:
            items.append({
                "id": str(pr.id),
                "return_number": pr.return_number,
                "purchase_order": {
                    "id": str(pr.purchase_order_id),
                    "po_number": pr.purchase_order.po_number if pr.purchase_order else None
                } if pr.purchase_order_id else None,
                "goods_receipt": {
                    "id": str(pr.goods_receipt_id),
                    "receipt_number": pr.goods_receipt.receipt_number if pr.goods_receipt else None
                } if pr.goods_receipt_id else None,
                "supplier": {
                    "id": str(pr.supplier_id),
                    "name": pr.supplier.name if pr.supplier else None,
                    "code": pr.supplier.code if pr.supplier else None
                } if pr.supplier_id else None,
                "warehouse": {
                    "id": str(pr.warehouse_id),
                    "name": pr.warehouse.name if pr.warehouse else None,
                    "code": pr.warehouse.code if pr.warehouse else None
                } if pr.warehouse_id else None,
                "return_date": pr.return_date.isoformat() if pr.return_date else None,
                "shipped_date": pr.shipped_date.isoformat() if pr.shipped_date else None,
                "status": pr.status,
                "return_type": pr.return_type,
                "total_return_amount": pr.total_return_amount,
                "refund_amount": pr.refund_amount,
                "total_items": len(pr.return_details) if pr.return_details else 0,
                "approved_by": str(pr.approved_by) if pr.approved_by else None,
                "approved_at": pr.approved_at.isoformat() if pr.approved_at else None,
                "completed_at": pr.completed_at.isoformat() if pr.completed_at else None,
                "confirmed_at": pr.confirmed_at.isoformat() if pr.confirmed_at else None,
                "created_at": pr.created_at.isoformat()
            })

        return {
            "data": items,
            "total": total,
        }
