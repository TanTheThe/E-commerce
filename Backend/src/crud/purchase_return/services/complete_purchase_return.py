from datetime import datetime
from typing import Optional
from src.crud.purchase_return.services.utils_service import UtilsPRService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.purchase_return import PurchaseReturnException


utils_pr_service = UtilsPRService()


class CompletePurchaseReturnService:
    async def complete_purchase_return(self, session: AsyncSession,
                                       purchase_return_id: str,
                                       shipped_date: Optional[datetime] = None,
                                       refund_amount: Optional[int] = None,
                                       notes: Optional[str] = None):
        pr = await utils_pr_service.validate_and_get_pr(session, purchase_return_id)

        if pr.status not in ["approved"]:
            PurchaseReturnException.only_complete_when_approved()

        pr.status = "completed"
        pr.completed_at = datetime.now()
        pr.shipped_date = shipped_date or datetime.now()

        if refund_amount is not None:
            pr.refund_amount = refund_amount
        else:
            if pr.return_type == "exchange":
                pr.refund_amount = 0
            else:
                pr.refund_amount = pr.total_return_amount

        if notes:
            pr.notes = (pr.notes or "") + f"\n[Hoàn tất] {notes}"

        pr.updated_at = datetime.now()

        await session.commit()
        await session.refresh(pr)

        return {
            "id": str(pr.id),
            "return_number": pr.return_number,
            "status": pr.status,
            "shipped_date": pr.shipped_date.isoformat() if pr.shipped_date else None,
            "completed_at": pr.completed_at.isoformat(),
            "total_return_amount": pr.total_return_amount,
            "refund_amount": pr.refund_amount,
            "return_type": pr.return_type,
        }
