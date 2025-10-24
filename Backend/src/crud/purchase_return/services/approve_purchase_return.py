from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.purchase_return.services.utils_service import UtilsPRService
from src.crud.supplier.repositories import SupplierRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Product_Variant, PurchaseOrderDetail, PurchaseOrder, PurchaseReturn
from src.errors.purchase_order import PurchaseOrderException
from src.errors.purchase_return import PurchaseReturnException
from src.schemas.purchase_order import ApprovePurchaseOrderRequest

purchase_return_repository = PurchaseReturnRepository()
utils_pr_service = UtilsPRService()


class PurchaseReturnApprovalService:
    async def approve_purchase_return(self, session: AsyncSession, purchase_return_id: str, approved_by: str):
        pr = await utils_pr_service.validate_and_get_pr(session, purchase_return_id)

        if pr.status != "draft":
            PurchaseReturnException.only_approved_when_draft()

        delivery_note_number = await purchase_return_repository.generate_delivery_note_number(session)

        pr.status = "approved"
        pr.approved_by = approved_by
        pr.approved_at = datetime.now()
        pr.delivery_note_number = delivery_note_number
        pr.updated_at = datetime.now()

        await session.commit()
        await session.refresh(pr)

        return {
            "id": str(pr.id),
            "return_number": pr.return_number,
            "old_status": "draft",
            "new_status": pr.status,
            "approved_by": str(pr.approved_by),
            "approved_at": pr.approved_at.isoformat(),
            "delivery_note_number": delivery_note_number,
            "next_step": "Gửi email thông báo cho NCC qua API /purchase-returns/{id}/send-email"
        }
