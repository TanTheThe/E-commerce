from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.database.models import GoodsReceipt
from src.schemas.purchase_return import SortBy


purchase_return_repository = PurchaseReturnRepository()

class GetAllGoodsReceiptService:
    async def get_all_goods_receipts(self, session: AsyncSession, warehouse_id: str, status_gr: Optional[str] = None,
                                     purchase_order_id: Optional[str] = None, supplier_id: Optional[str] = None,
                                     from_date: Optional[datetime] = None, to_date: Optional[datetime] = None,
                                     search: Optional[str] = None, sort_by: Optional[SortBy] = None,
                                     skip: int = 0, limit: int = 10):
        conditions = [GoodsReceipt.warehouse_id == warehouse_id]

        if status_gr:
            conditions.append(GoodsReceipt.status == status_gr)

        if purchase_order_id:
            conditions.append(
                GoodsReceipt.purchase_order_id == purchase_order_id)

        if supplier_id:
            conditions.append(GoodsReceipt.supplier_id == supplier_id)

        if from_date:
            conditions.append(GoodsReceipt.receipt_date >= from_date)

        if to_date:
            conditions.append(GoodsReceipt.receipt_date <= to_date)

        if search:
            conditions.append(
                GoodsReceipt.receipt_number.ilike(f"%{search}%")
            )

        options = [
            selectinload(GoodsReceipt.purchase_order),
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.receipt_details)
        ]

        sort_by_result = None
        if not sort_by:
            sort_by_result = desc(GoodsReceipt.created_at)
        elif sort_by == "receipt_date_asc":
            sort_by_result = asc(GoodsReceipt.receipt_date)
        elif sort_by == "receipt_date_desc":
            sort_by_result = desc(GoodsReceipt.receipt_date)
        elif sort_by == "created_at_asc":
            sort_by_result = asc(GoodsReceipt.created_at)
        elif sort_by == "created_at_desc":
            sort_by_result = desc(GoodsReceipt.created_at)
        elif sort_by == "total_amount_asc":
            sort_by_result = asc(GoodsReceipt.total_received_amount)
        elif sort_by == "total_amount_desc":
            sort_by_result = desc(GoodsReceipt.total_received_amount)

        grs, total = await purchase_return_repository.get_all_purchase_returns(session=session, where_conditions=conditions,
                                                                               order_by=sort_by_result, skip=skip,
                                                                               limit=limit, options=options)

        items = []
        for gr in grs:
            items.append({
                "id": str(gr.id),
                "receipt_number": gr.receipt_number,
                "purchase_order": {
                    "id": str(gr.purchase_order_id),
                    "po_number": gr.purchase_order.po_number if gr.purchase_order else None
                } if gr.purchase_order_id else None,
                "supplier": {
                    "id": str(gr.supplier_id),
                    "name": gr.supplier.name if gr.supplier else None,
                    "code": gr.supplier.code if gr.supplier else None
                } if gr.supplier_id else None,
                "warehouse": {
                    "id": str(gr.warehouse_id),
                    "name": gr.warehouse.name if gr.warehouse else None,
                    "code": gr.warehouse.code if gr.warehouse else None
                } if gr.warehouse_id else None,
                "receipt_date": gr.receipt_date.isoformat() if gr.receipt_date else None,
                "status": gr.status,
                "total_received_amount": gr.total_received_amount,
                "total_items": len(gr.receipt_details) if gr.receipt_details else 0,
                "parent_receipt_id": str(gr.parent_receipt_id) if gr.parent_receipt_id else None,
                "approved_by": str(gr.approved_by) if gr.approved_by else None,
                "approved_at": gr.approved_at.isoformat() if gr.approved_at else None,
                "completed_at": gr.completed_at.isoformat() if gr.completed_at else None,
                "created_at": gr.created_at.isoformat()
            })

        return {
            "data": items,
            "total": total,
        }
