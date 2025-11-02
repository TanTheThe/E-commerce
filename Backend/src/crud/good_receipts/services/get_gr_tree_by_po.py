from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.user.repositories import UserRepository
from src.database.models import GoodsReceipt, PurchaseOrder
from src.errors.purchase_order import PurchaseOrderException

goods_receipt_repository = GoodsReceiptRepository()
purchase_order_repository = PurchaseOrderRepository()
user_repository = UserRepository()


class GetGRTreeByPOService:
    async def get_gr_tree_by_po(self, purchase_order_id: str, warehouse_id: str, session: AsyncSession):
        po = await purchase_order_repository.get_purchase_order(
            session=session, where_conditions=[PurchaseOrder.id == purchase_order_id]
        )

        if not po:
            PurchaseOrderException.po_not_found()

        conditions = [GoodsReceipt.purchase_order_id == purchase_order_id, GoodsReceipt.warehouse_id == warehouse_id]

        options = [
            selectinload(GoodsReceipt.receipt_details),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.supplier)
        ]

        grs, _ = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=conditions,
            options=options
        )

        tree = self.build_gr_tree(grs)

        return {
            "purchase_order_id": str(po.id),
            "receipts_tree": tree,
            "total_receipts": len(grs)
        }

    def build_gr_tree(self, grs: List[GoodsReceipt]):
        if not grs:
            return []

        gr_map = {str(gr.id): gr for gr in grs}

        root_grs = [gr for gr in grs if gr.parent_receipt_id is None]

        def build_node(gr: GoodsReceipt) -> dict:
            gr_id = str(gr.id)
            parent_id = str(gr.parent_receipt_id) if gr.parent_receipt_id else None

            parent_gr = gr_map.get(parent_id) if parent_id else None
            receipt_number_parent = parent_gr.receipt_number if parent_gr else None

            children_grs = [
                g for g in grs
                if g.parent_receipt_id and str(g.parent_receipt_id) == gr_id
            ]

            children_nodes = [build_node(child) for child in children_grs]

            return {
                "id": gr_id,
                "receipt_number": gr.receipt_number,
                "receipt_number_parent": receipt_number_parent,
                "status": gr.status,
                "receipt_date": gr.receipt_date.isoformat() if gr.receipt_date else None,
                "total_received_amount": gr.total_received_amount,
                "total_items": len(gr.receipt_details) if gr.receipt_details else 0,
                "has_discrepancy": gr.has_discrepancy,
                "parent_receipt_id": str(gr.parent_receipt_id) if gr.parent_receipt_id else None,
                "supplier": {
                    "id": str(gr.supplier_id),
                    "name": gr.supplier.name if gr.supplier else None,
                    "code": gr.supplier.code if gr.supplier else None
                } if gr.supplier_id and gr.supplier else None,
                "warehouse": {
                    "id": str(gr.warehouse_id),
                    "name": gr.warehouse.name if gr.warehouse else None,
                    "code": gr.warehouse.code if gr.warehouse else None
                } if gr.warehouse_id and gr.warehouse else None,
                "approved_by": str(gr.approved_by) if gr.approved_by else None,
                "approved_at": gr.approved_at.isoformat() if gr.approved_at else None,
                "completed_at": gr.completed_at.isoformat() if gr.completed_at else None,
                "created_at": gr.created_at.isoformat(),
                "children": children_nodes
            }

        tree = [build_node(root) for root in root_grs]

        return tree
