from datetime import datetime
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.purchase_return.services.utils_service import UtilsPRService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.purchase_return import PurchaseReturnException
import logging

logger = logging.getLogger(__name__)

purchase_return_repository = PurchaseReturnRepository()
utils_pr_service = UtilsPRService()


class PurchaseReturnApprovalService:
    async def approve_purchase_return(self, session: AsyncSession, purchase_return_id: str, approved_by: str):
        pr = await utils_pr_service.validate_and_get_pr(session, purchase_return_id, minimal=True)

        if pr.status != "draft":
            PurchaseReturnException.only_approved_when_draft()
        
        try:
            delivery_note_number = await purchase_return_repository.generate_delivery_note_number(session)
            
            update_data = {
                "status": "approved",
                "approved_by": approved_by,
                "approved_at": datetime.now(),
                "delivery_note_number": delivery_note_number,
                "updated_at": datetime.now()
            }
            
            for key, value in update_data.items():
                setattr(pr, key, value)

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
        
        except Exception as e:
            await session.rollback()
            logger.error("Error approved purchase return: ", e)
            PurchaseReturnException.error_while_approve_pr()
