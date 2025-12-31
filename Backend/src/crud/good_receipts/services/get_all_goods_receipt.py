from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import asc, desc, or_
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.database.models import GoodsReceipt
from src.schemas.goods_receipt import GetAllGoodsReceiptsQueryParams
from src.schemas.purchase_return import SortBy


goods_receipt_repository = GoodsReceiptRepository()

class GetAllGoodsReceiptService:
    async def get_all_goods_receipts(self, session: AsyncSession, params: GetAllGoodsReceiptsQueryParams,
                                     skip: int = 0, limit: int = 10):
        conditions = [GoodsReceipt.warehouse_id == params.warehouse_id]

        if params.status_gr:
            conditions.append(GoodsReceipt.status == params.status_gr.value)

        if params.purchase_order_id:
            conditions.append(GoodsReceipt.purchase_order_id == params.purchase_order_id)

        if params.supplier_id:
            conditions.append(GoodsReceipt.supplier_id == params.supplier_id)

        if params.from_date:
            conditions.append(GoodsReceipt.receipt_date >= params.from_date)

        if params.to_date:
            end_of_day = params.to_date.replace(hour=23, minute=59, second=59)
            conditions.append(GoodsReceipt.receipt_date <= end_of_day)

        if params.search:
            search_pattern = f"%{params.search}%"
            conditions.append(
                or_(
                    GoodsReceipt.receipt_number.ilike(search_pattern),
                    GoodsReceipt.delivery_note_number.ilike(search_pattern)
                )
            )

        options = [
            selectinload(GoodsReceipt.purchase_order),
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.receipt_details)
        ]

        if not params.sort_by:
            return desc(GoodsReceipt.created_at)

        sort_mapping = {
            SortBy.RECEIPT_DATE_ASC: asc(GoodsReceipt.receipt_date),
            SortBy.RECEIPT_DATE_DESC: desc(GoodsReceipt.receipt_date),
            SortBy.CREATED_AT_ASC: asc(GoodsReceipt.created_at),
            SortBy.CREATED_AT_DESC: desc(GoodsReceipt.created_at),
            SortBy.TOTAL_AMOUNT_ASC: asc(GoodsReceipt.total_received_amount),
            SortBy.TOTAL_AMOUNT_DESC: desc(GoodsReceipt.total_received_amount),
        }

        sort_order = sort_mapping.get(params.sort_by, desc(GoodsReceipt.created_at))

        grs, total = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=conditions,
            order_by=sort_order,
            skip=skip,
            limit=limit,
            options=options
        )

        parent_ids = [gr.parent_receipt_id for gr in grs if gr.parent_receipt_id]

        parent_map = {}
        if parent_ids:
            parent_receipts, _ = await goods_receipt_repository.get_all_goods_receipt(
                session=session,
                where_conditions=[GoodsReceipt.id.in_(parent_ids)]
            )
            parent_map = {str(r.id): r.receipt_number for r in parent_receipts}

        items = []
        for gr in grs:
            parent_id = str(gr.parent_receipt_id) if gr.parent_receipt_id else None
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
                "has_discrepancy": gr.has_discrepancy,
                "parent_receipt_id": parent_id,
                "receipt_number_parent": parent_map.get(parent_id),
                "approved_by": str(gr.approved_by) if gr.approved_by else None,
                "approved_at": gr.approved_at.isoformat() if gr.approved_at else None,
                "completed_at": gr.completed_at.isoformat() if gr.completed_at else None,
                "created_at": gr.created_at.isoformat()
            })

        return {
            "data": items,
            "total": total,
        }
