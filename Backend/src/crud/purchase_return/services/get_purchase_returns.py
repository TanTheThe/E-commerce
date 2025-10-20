from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.database.models import GoodsReceipt, PurchaseReturn, Warehouse
from src.schemas.purchase_return import SortBy


purchase_return_repository = PurchaseReturnRepository()


class GetPurchaseReturnsService:
    async def get_purchase_returns(self, session: AsyncSession,
                                   warehouse_id: str,
                                   status_pr: Optional[str] = None,
                                   purchase_order_id: Optional[str] = None,
                                   goods_receipt_id: Optional[str] = None,
                                   supplier_id: Optional[str] = None,
                                   from_date: Optional[datetime] = None,
                                   to_date: Optional[datetime] = None,
                                   search: Optional[str] = None,
                                   sort_by: Optional[SortBy] = None,
                                   skip: int = 0, limit: int = 10):
        conditions = [Warehouse.id == warehouse_id]

        if status_pr:
            conditions.append(PurchaseReturn.status == status_pr)

        if purchase_order_id:
            conditions.append(
                PurchaseReturn.purchase_order_id == purchase_order_id)

        if goods_receipt_id:
            conditions.append(
                PurchaseReturn.goods_receipt_id == goods_receipt_id)

        if supplier_id:
            conditions.append(PurchaseReturn.supplier_id == supplier_id)

        if from_date:
            conditions.append(PurchaseReturn.return_date >= from_date)

        if to_date:
            conditions.append(PurchaseReturn.return_date <= to_date)

        options = [
            selectinload(PurchaseReturn.purchase_order),
            selectinload(PurchaseReturn.supplier),
            selectinload(PurchaseReturn.warehouse),
            selectinload(PurchaseReturn.goods_receipt).selectinload(
                GoodsReceipt.receipt_details),
            selectinload(PurchaseReturn.return_details)
        ]

        sort_by_result = None
        if not sort_by:
            sort_by_result = desc(PurchaseReturn.return_date)
        elif sort_by == "return_date_asc":
            sort_by_result = asc(PurchaseReturn.return_date)
        elif sort_by == "return_date_desc":
            sort_by_result = desc(PurchaseReturn.return_date)
        elif sort_by == "total_return_amount_asc":
            sort_by_result = asc(PurchaseReturn.total_return_amount)
        elif sort_by == "total_return_amount_asc":
            sort_by_result = desc(PurchaseReturn.total_return_amount)

        prs, total = await purchase_return_repository.get_all_purchase_returns(session=session, where_conditions=conditions,
                                                                               order_by=sort_by_result, skip=skip,
                                                                               limit=limit, options=options)

        items = []
        for pr in prs:
            items.append(
                {
                    "id": str(pr.id),
                    "return_number": pr.return_number,
                    "purchase_order": {
                        "id": str(pr.purchase_order_id),
                        "po_number": pr.purchase_order.po_number if pr.purchase_order else None
                    } if pr.purchase_order_id else None,
                    "warehouse": {
                        "id": str(pr.warehouse_id),
                        "name": pr.warehouse.name if pr.warehouse else None,
                        "code": pr.warehouse.code if pr.warehouse else None
                    } if pr.warehouse_id else None,
                    "goods_receipt": {
                        "id": str(pr.goods_receipt_id),
                        "receipt_number": pr.goods_receipt.receipt_number if pr.goods_receipt else None
                    } if pr.goods_receipt else None,
                    "supplier": {
                        "id": str(pr.supplier_id),
                        "name": pr.supplier.name if pr.supplier else None,
                        "code": pr.supplier.code if pr.supplier else None
                    } if pr.supplier_id else None,
                    "return_type": pr.return_type,
                    "return_date": pr.return_date.isoformat() if pr.return_date else None,
                    "status": pr.status,
                    "total_return_amount": pr.total_return_amount,
                    "approved_by": str(pr.approved_by) if pr.approved_by else None,
                    "approved_at": pr.approved_at.isoformat() if pr.approved_at else None,
                    "completed_at": pr.completed_at.isoformat() if pr.completed_at else None,
                }
            )

        return {
            "data": items,
            "total": total,
        }
