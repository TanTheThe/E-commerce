from sqlalchemy.orm import selectinload
from sqlmodel import or_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.database.models import GoodsReceipt
from src.errors.goods_receipt import GoodsReceiptException

goods_receipt_repository = GoodsReceiptRepository()


class UtilsGRService:
    async def get_all_related_receipts(self, current_gr: GoodsReceipt, po_id: str, session: AsyncSession):
        root_id = await self.find_root_receipt(current_gr, session)

        condition = [
            GoodsReceipt.purchase_order_id == po_id,
            GoodsReceipt.id == root_id
        ]

        options = [selectinload(GoodsReceipt.receipt_details)]

        grs, _ = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=condition,
            options=options
        )
        
        all_grs = await self.get_all_descendants_recursively(grs, po_id, session)
        
        return all_grs

    async def find_root_receipt(self, current_gr: GoodsReceipt, session: AsyncSession):
        visited = set()
        current = current_gr

        while current and current.parent_receipt_id is not None:
            parent_id_str = str(current.parent_receipt_id)

            if parent_id_str in visited:
                GoodsReceiptException.circular_gr_error()

            visited.add(parent_id_str)

            parent = await goods_receipt_repository.get_goods_receipt(
                session=session,
                where_conditions=[GoodsReceipt.id == current.parent_receipt_id],
            )

            if not parent:
                return str(current.id)

            current = parent

            if parent.parent_receipt_id is None:
                return str(parent.id)

            await session.refresh(current)

        return str(current.id)


    async def get_all_descendants_recursively(self, current_grs, po_id: str, session: AsyncSession):
        all_grs = list(current_grs)

        visited_ids = set(str(gr.id) for gr in current_grs)

        current_batch = list(current_grs)

        while current_batch:
            current_ids = [str(gr.id) for gr in current_batch]

            condition = [
                GoodsReceipt.purchase_order_id == po_id,
                GoodsReceipt.parent_receipt_id.in_(current_ids)
            ]

            options = [selectinload(GoodsReceipt.receipt_details)]

            children, _ = await goods_receipt_repository.get_all_goods_receipt(
                session=session,
                where_conditions=condition,
                options=options
            )

            if not children:
                break

            new_children = []
            for child in children:
                child_id = str(child.id)
                if child_id in visited_ids:
                    GoodsReceiptException.circular_gr_error()

                visited_ids.add(child_id)
                new_children.append(child)

            all_grs.extend(new_children)
            current_batch = new_children

        return all_grs

    def calculate_total_accepted_quantity(self, all_related_grs: list, current_gr: GoodsReceipt):
        variant_summary = {}

        for related_gr in all_related_grs:
            for detail in related_gr.receipt_details:
                variant_id = str(detail.product_variant_id)
                po_detail_id = str(detail.po_detail_id)

                if variant_id not in variant_summary:
                    variant_summary[variant_id] = {
                        'po_detail_id': po_detail_id,
                        'total_accepted': 0
                    }

                if related_gr.id == current_gr.id:
                    variant_summary[variant_id]['total_accepted'] += detail.accepted_quantity
                elif related_gr.status in ['approved', 'completed', 'has_issue']:
                    variant_summary[variant_id]['total_accepted'] += detail.accepted_quantity

        return variant_summary

    def determine_status_based_on_po(self, variant_summary: dict, po_details_map: dict):
        all_completed = True
        comparison_details = []

        for variant_id, summary in variant_summary.items():
            po_detail_id = summary['po_detail_id']
            po_detail = po_details_map.get(po_detail_id)

            if not po_detail:
                continue

            ordered_qty = po_detail.quantity
            total_accepted_qty = summary['total_accepted']

            comparison_details.append({
                'variant_id': variant_id,
                'po_detail_id': po_detail_id,
                'ordered': ordered_qty,
                'total_accepted': total_accepted_qty,
                'is_complete': total_accepted_qty >= ordered_qty
            })

            if total_accepted_qty < ordered_qty:
                all_completed = False

        gr_status = "completed" if all_completed else "has_issue"

        return {
            'gr_status': gr_status,
            'all_completed': all_completed,
            'comparison_details': comparison_details
        }
        
    async def validate_draft_status(self, session: AsyncSession, goods_receipt_id: str):
        condition = [GoodsReceipt.id == goods_receipt_id]
        options = [selectinload(GoodsReceipt.receipt_details)]

        gr = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=condition,
            options=options
        )

        if not gr:
            GoodsReceiptException.gr_not_found()

        if gr.status != "pending":
            GoodsReceiptException.only_update_delete_when_draft()

        return gr
