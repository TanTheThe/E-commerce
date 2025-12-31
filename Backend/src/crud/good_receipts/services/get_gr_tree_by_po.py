from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import GoodsReceipt, PurchaseOrder, Warehouse
from src.errors.purchase_order import PurchaseOrderException
from src.errors.warehouse import WareHouseException

goods_receipt_repository = GoodsReceiptRepository()
purchase_order_repository = PurchaseOrderRepository()
user_repository = UserRepository()
warehouse_repository = WareHouseRepository()


class GetGRTreeByPOService:
    async def get_gr_tree_by_po(self, purchase_order_id: str, warehouse_id: str, session: AsyncSession):
        po = await purchase_order_repository.get_purchase_order(
            session=session, where_conditions=[PurchaseOrder.id == purchase_order_id]
        )

        if not po:
            PurchaseOrderException.po_not_found()

        warehouse = await warehouse_repository.get_warehouse(
            session=session,
            where_conditions=[Warehouse.id == warehouse_id]
        )

        if not warehouse:
            WareHouseException.warehouse_not_found()

        conditions = [
            GoodsReceipt.purchase_order_id == purchase_order_id,
            GoodsReceipt.warehouse_id == warehouse_id
        ]

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

        if not grs:
            return {
                "purchase_order_id": str(po.id),
                "purchase_order_number": po.po_number,
                "warehouse_id": warehouse_id,
                "warehouse_name": warehouse.name,
                "receipts_tree": [],
                "total_receipts": 0,
                "total_root_receipts": 0,
                "total_child_receipts": 0
            }

        tree = self.build_gr_tree(grs)

        root_count = sum(1 for gr in grs if gr.parent_receipt_id is None)
        child_count = len(grs) - root_count

        return {
            "purchase_order_id": str(po.id),
            "purchase_order_number": po.po_number,
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse.name,
            "receipts_tree": tree,
            "total_receipts": len(grs),
            "total_root_receipts": root_count,
            "total_child_receipts": child_count
        }


    def build_gr_tree(self, grs: List[GoodsReceipt]):
        if not grs:
            return []

        gr_map = {str(gr.id): gr for gr in grs}
        children_map = {}

        for gr in grs:
            if gr.parent_receipt_id:
                parent_id = str(gr.parent_receipt_id)
                if parent_id not in children_map:
                    children_map[parent_id] = []
                children_map[parent_id].append(gr)

        root_grs = [gr for gr in grs if gr.parent_receipt_id is None]

        def build_node(gr: GoodsReceipt, depth: int = 0) -> dict:
            gr_id = str(gr.id)

            parent_id = str(gr.parent_receipt_id) if gr.parent_receipt_id else None
            parent_gr = gr_map.get(parent_id) if parent_id else None
            receipt_number_parent = parent_gr.receipt_number if parent_gr else None

            children_grs = children_map.get(gr_id, [])
            children_nodes = [build_node(child, depth + 1) for child in children_grs]

            total_received = sum(
                detail.received_quantity
                for detail in gr.receipt_details
            ) if gr.receipt_details else 0

            total_accepted = sum(
                detail.accepted_quantity
                for detail in gr.receipt_details
            ) if gr.receipt_details else 0

            total_rejected = sum(
                detail.rejected_quantity
                for detail in gr.receipt_details
            ) if gr.receipt_details else 0

            return {
                "id": gr_id,
                "receipt_number": gr.receipt_number,
                "receipt_number_parent": receipt_number_parent,
                "parent_receipt_id": parent_id,
                "status": gr.status,
                "receipt_date": gr.receipt_date.isoformat() if gr.receipt_date else None,
                "total_received_amount": float(gr.total_received_amount) if gr.total_received_amount else 0,
                "total_items": len(gr.receipt_details) if gr.receipt_details else 0,
                "total_received_quantity": total_received,
                "total_accepted_quantity": total_accepted,
                "total_rejected_quantity": total_rejected,
                "has_discrepancy": gr.has_discrepancy,
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
                "created_at": gr.created_at.isoformat() if gr.created_at else None,
                "depth": depth,
                "has_children": len(children_nodes) > 0,
                "children_count": len(children_nodes),
                "children": children_nodes
            }

        tree = [build_node(root) for root in root_grs]

        return tree
