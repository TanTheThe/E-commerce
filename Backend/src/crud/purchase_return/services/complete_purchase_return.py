from datetime import datetime
from typing import Optional
from src.crud.purchase_return.services.utils_service import UtilsPRService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.purchase_return import PurchaseReturnException


utils_pr_service = UtilsPRService()


class CompletePurchaseReturnService:
    async def complete_purchase_return(self, session: AsyncSession,
                                       purchase_return_id: str,
                                       completed_by: Optional[str] = None):
        pr = await utils_pr_service.validate_and_get_pr(session, purchase_return_id)

        if pr.status != "confirmed":
            PurchaseReturnException.only_complete_when_confirmed()

        if not pr.return_details:
            PurchaseReturnException.no_return_details_found()

        pr.status = "completed"
        pr.completed_at = datetime.now()
        pr.shipped_date = datetime.now()
        pr.completed_by = completed_by
        pr.updated_at = datetime.now()
        session.add(pr)

        await session.flush()

        affected_gr_ids = {str(d.goods_receipt_detail_id) for d in pr.return_details if d.goods_receipt_detail_id}
        for gr_detail_id in affected_gr_ids:
            await utils_pr_service.sync_returned_quantity(session, gr_detail_id)

        await session.commit()
        await session.refresh(pr)

        return {
            "id": str(pr.id),
            "return_number": pr.return_number,
            "status": pr.status,
            "shipped_date": pr.shipped_date.isoformat() if pr.shipped_date else None,
            "completed_at": pr.completed_at.isoformat(),
        }
