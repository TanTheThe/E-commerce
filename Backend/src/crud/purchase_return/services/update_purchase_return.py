from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy.orm import selectinload
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.purchase_return.services.utils_service import UtilsPRService
from src.crud.supplier.repositories import SupplierRepository
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import PurchaseOrder, PurchaseOrderDetail, Product_Variant, Supplier, Warehouse, \
    PurchaseReturn, PurchaseReturnDetail
from src.errors.product import ProductException
from src.errors.purchase_order import PurchaseOrderException
from src.errors.supplier import SupplierException
from src.errors.warehouse import WareHouseException
from src.schemas.purchase_order import UpdatePurchaseOrderRequest

utils_pr_service = UtilsPRService()

class UpdatePurchaseReturnService:
    async def update_purchase_return(self, session: AsyncSession, purchase_return_id: str, update_data: Dict[str, Any]):
        pr = await utils_pr_service.validate_draft_status(session, purchase_return_id)

        if "return_date" in update_data:
            pr.return_date = update_data["return_date"]

        if "return_type" in update_data:
            pr.return_type = update_data["return_type"]

        if "return_reason" in update_data:
            pr.return_reason = update_data["return_reason"]

        if "delivery_note_number" in update_data:
            pr.delivery_note_number = update_data["delivery_note_number"]

        if "refund_amount" in update_data:
            pr.refund_amount = update_data["refund_amount"]

        if "notes" in update_data:
            pr.notes = update_data["notes"]

        if "return_details" in update_data:
            await self.update_return_details(
                session=session,
                pr=pr,
                details_data=update_data["return_details"]
            )

        total_return_amount = sum(d.total_cost for d in pr.return_details)
        pr.total_return_amount = total_return_amount

        pr.updated_at = datetime.now()

        await session.commit()
        await session.refresh(pr)

        return {
            "id": str(pr.id),
            "return_number": pr.return_number,
            "total_return_amount": pr.total_return_amount,
            "refund_amount": pr.refund_amount,
            "updated_at": pr.updated_at
        }

    async def update_return_details(self, session: AsyncSession, pr: PurchaseReturn, details_data: List[Dict[str, Any]]):
        existing_detail_ids = {str(d.id) for d in pr.return_details}
        updated_detail_ids = set()

        for detail_data in details_data:
            detail_id = detail_data.get("id")

            return_qty = detail_data["return_quantity"]
            unit_cost = detail_data["unit_cost"]
            total_cost = return_qty * unit_cost

            if detail_id and detail_id in existing_detail_ids:
                detail = next(d for d in pr.return_details if str(d.id) == detail_id)
                detail.product_variant_id = detail_data["product_variant_id"]
                detail.goods_receipt_detail_id = detail_data.get("goods_receipt_detail_id")
                detail.return_quantity = detail_data["return_quantity"]
                detail.unit_cost = detail_data["unit_cost"]
                detail.total_cost = total_cost
                detail.condition = detail_data.get("condition")
                detail.rejection_evidence = detail_data.get("rejection_evidence")
                detail.notes = detail_data.get("notes")

                updated_detail_ids.add(detail_id)
            else:
                new_detail = PurchaseReturnDetail(
                    purchase_return_id=pr.id,
                    product_variant_id=detail_data["product_variant_id"],
                    goods_receipt_detail_id=detail_data.get("goods_receipt_detail_id"),
                    return_quantity=detail_data["return_quantity"],
                    unit_cost=detail_data["unit_cost"],
                    total_cost=total_cost,
                    condition=detail_data.get("condition"),
                    rejection_evidence=detail_data.get("rejection_evidence"),
                    notes=detail_data.get("notes"),
                )
                session.add(new_detail)
                pr.return_details.append(new_detail)

        # Xóa các details không còn trong danh sách update
        details_to_delete = existing_detail_ids - updated_detail_ids
        if details_to_delete:
            for detail in pr.return_details[:]:  # Copy list to avoid modification during iteration
                if str(detail.id) in details_to_delete:
                    await session.delete(detail)
                    pr.return_details.remove(detail)









