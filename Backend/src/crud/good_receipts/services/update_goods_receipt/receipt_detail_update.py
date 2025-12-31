from datetime import datetime
from typing import List, Dict
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.services.update_goods_receipt.update_gr_validation import UpdateGRValidationService
from src.database.models import GoodsReceiptDetail
from src.schemas.goods_receipt import ReceiptDetailUpdate


validation_service = UpdateGRValidationService()

class ReceiptDetailUpdateService:
    async def update_receipt_details(self, gr, details_data: List[ReceiptDetailUpdate], variants_map: Dict[str, any],
                                     po_details_map: Dict[str, any], session: AsyncSession):
        existing_detail_ids = {str(d.id) for d in gr.receipt_details}
        updated_detail_ids = set()

        for detail_data in details_data:
            detail_id = detail_data.id

            accepted_qty = detail_data.accepted_quantity
            unit_cost = detail_data.unit_cost
            total_cost = accepted_qty * unit_cost

            variant = variants_map[detail_data.product_variant_id]
            po_detail = po_details_map[detail_data.po_detail_id]

            if detail_id and detail_id in existing_detail_ids:
                detail = next(
                    d for d in gr.receipt_details
                    if str(d.id) == detail_id
                )

                self.update_detail(detail, detail_data, total_cost, variant, po_detail)

                updated_detail_ids.add(detail_id)
            else:
                new_detail = self.create_detail(
                    gr,
                    detail_data,
                    total_cost,
                    variant,
                    po_detail
                )

                session.add(new_detail)
                gr.receipt_details.append(new_detail)

        details_to_delete = existing_detail_ids - updated_detail_ids
        if not details_to_delete:
            return

        for detail in gr.receipt_details[:]:
            if str(detail.id) in details_to_delete:
                await session.delete(detail)
                gr.receipt_details.remove(detail)

        return len(details_to_delete)


    def update_detail(self, detail, detail_data: ReceiptDetailUpdate, total_cost: int, variant: any, po_detail: any):
        detail.product_variant_id = detail_data.product_variant_id
        detail.po_detail_id = detail_data.po_detail_id
        detail.ordered_quantity = detail_data.ordered_quantity
        detail.received_quantity = detail_data.received_quantity
        detail.accepted_quantity = detail_data.accepted_quantity
        detail.rejected_quantity = detail_data.rejected_quantity
        detail.unit_cost = detail_data.unit_cost
        detail.total_cost = total_cost
        detail.rejection_reason = detail_data.rejection_reason
        detail.notes = detail_data.notes
        detail.updated_at = datetime.now()

        product_snapshot = {
            "product_name": variant.product.name if variant.product else None,
            "variant_sku": variant.sku,
            "variant_size": variant.size,
            "variant_color_name": variant.color_name if variant.color_name else (
                variant.color.name if variant.color else None
            ),
            "variant_color_code": variant.color_code if variant.color_code else (
                variant.color.code if variant.color else None
            ),
            "variant_image": variant.image,
            "variant_price": variant.price,
            "unit_cost": detail_data.unit_cost,
            "snapshot_date": datetime.now().isoformat()
        }

        detail.product_snapshot = product_snapshot


    def create_detail(self, gr, detail_data: ReceiptDetailUpdate, total_cost: int, variant: any, po_detail: any):
        product_snapshot = {
            "product_name": variant.product.name if variant.product else None,
            "variant_sku": variant.sku,
            "variant_size": variant.size,
            "variant_color_name": variant.color_name if variant.color_name else (
                variant.color.name if variant.color else None
            ),
            "variant_color_code": variant.color_code if variant.color_code else (
                variant.color.code if variant.color else None
            ),
            "variant_image": variant.image,
            "variant_price": variant.price,
            "unit_cost": detail_data.unit_cost,
            "snapshot_date": datetime.now().isoformat()
        }

        return GoodsReceiptDetail(
            goods_receipt_id=gr.id,
            product_variant_id=detail_data.product_variant_id,
            po_detail_id=detail_data.po_detail_id,
            ordered_quantity=detail_data.ordered_quantity,
            received_quantity=detail_data.received_quantity,
            accepted_quantity=detail_data.accepted_quantity,
            rejected_quantity=detail_data.rejected_quantity,
            unit_cost=detail_data.unit_cost,
            total_cost=total_cost,
            rejection_reason=detail_data.rejection_reason,
            product_snapshot=product_snapshot,
            notes=detail_data.notes,
            created_at=datetime.now()
        )

