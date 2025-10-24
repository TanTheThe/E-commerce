from datetime import datetime
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.purchase_return.services.utils_service import UtilsPRService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.purchase_return import PurchaseReturnException

purchase_return_repository = PurchaseReturnRepository()
utils_pr_service = UtilsPRService()


class PurchaseReturnConfirmedService:
    async def confirmed_purchase_return(self, session: AsyncSession, purchase_return_id: str, confirmed_by: str):
        pr = await utils_pr_service.validate_and_get_pr(session, purchase_return_id)

        if pr.status != "sent":
            PurchaseReturnException.only_confirmed_when_sent()

        pr.status = "confirmed"
        pr.confirmed_by = confirmed_by
        pr.confirmed_at = datetime.now()
        pr.updated_at = datetime.now()

        await session.commit()
        await session.refresh(pr)

        return {
            "id": str(pr.id),
            "return_number": pr.return_number,
            "old_status": "sent",
            "new_status": pr.status,
            "confirmed_by": str(pr.confirmed_by),
            "confirmed_at": pr.confirmed_at.isoformat(),
        }
