from datetime import datetime
from typing import Any, Dict, List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.good_receipts.services.utils_service import UtilsGRService
from src.database.models import GoodsReceipt, GoodsReceiptDetail
import uuid


goods_receipt_repository = GoodsReceiptRepository()
utils_gr_service = UtilsGRService()


class UpdateGoodsReceiptService:
    async def update_goods_receipt(self, session: AsyncSession, goods_receipt_id: str,
                                   update_data: Dict[str, Any]):
        gr = await utils_gr_service.validate_draft_status(session, goods_receipt_id)

        if "receipt_date" in update_data:
            gr.receipt_date = update_data["receipt_date"]

        if "delivery_note_number" in update_data:
            gr.delivery_note_number = update_data["delivery_note_number"]

        if "has_discrepancy" in update_data:
            gr.has_discrepancy = update_data["has_discrepancy"]

        if "discrepancy_notes" in update_data:
            gr.discrepancy_notes = update_data["discrepancy_notes"]

        if "notes" in update_data:
            gr.notes = update_data["notes"]

        if "receipt_details" in update_data:
            await self.update_receipt_details(
                session=session,
                gr=gr,
                details_data=update_data["receipt_details"]
            )

        total_received_amount = sum(d.total_cost for d in gr.receipt_details)
        gr.total_received_amount = total_received_amount

        gr.updated_at = datetime.now()

        await session.commit()
        await session.refresh(gr)

        return {
            "id": str(gr.id),
            "receipt_number": gr.receipt_number,
            "total_received_amount": gr.total_received_amount,
            "updated_at": gr.updated_at
        }

    async def update_receipt_details(self, session: AsyncSession, gr: GoodsReceipt,
                                     details_data: List[Dict[str, Any]]):
        existing_detail_ids = {str(d.id) for d in gr.receipt_details}
        updated_detail_ids = set()

        for detail_data in details_data:
            detail_id = detail_data.get("id")

            accepted_qty = detail_data["accepted_quantity"]
            unit_cost = detail_data["unit_cost"]
            total_cost = accepted_qty * unit_cost

            received_qty = detail_data["received_quantity"]
            rejected_qty = detail_data.get("rejected_quantity", 0)

            if rejected_qty != (received_qty - accepted_qty):
                detail_data["rejected_quantity"] = received_qty - accepted_qty

            if detail_id and detail_id in existing_detail_ids:
                detail = next(
                    d for d in gr.receipt_details if str(d.id) == detail_id)
                detail.product_variant_id = detail_data["product_variant_id"]
                detail.po_detail_id = detail_data["po_detail_id"]
                detail.ordered_quantity = detail_data["ordered_quantity"]
                detail.received_quantity = detail_data["received_quantity"]
                detail.accepted_quantity = detail_data["accepted_quantity"]
                detail.rejected_quantity = detail_data["rejected_quantity"]
                detail.unit_cost = detail_data["unit_cost"]
                detail.total_cost = total_cost
                detail.rejection_reason = detail_data.get("rejection_reason")
                detail.notes = detail_data.get("notes")

                updated_detail_ids.add(detail_id)
            else:
                new_detail = GoodsReceiptDetail(
                    id=uuid.uuid4(),
                    goods_receipt_id=gr.id,
                    product_variant_id=detail_data["product_variant_id"],
                    po_detail_id=detail_data["po_detail_id"],
                    ordered_quantity=detail_data["ordered_quantity"],
                    received_quantity=detail_data["received_quantity"],
                    accepted_quantity=detail_data["accepted_quantity"],
                    rejected_quantity=detail_data["rejected_quantity"],
                    unit_cost=detail_data["unit_cost"],
                    total_cost=total_cost,
                    rejection_reason=detail_data.get("rejection_reason"),
                    notes=detail_data.get("notes"),
                )
                session.add(new_detail)
                gr.receipt_details.append(new_detail)
