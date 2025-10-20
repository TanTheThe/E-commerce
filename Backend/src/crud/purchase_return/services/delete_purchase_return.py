from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.purchase_return.services.utils_service import UtilsPRService
from src.errors.purchase_return import PurchaseReturnException


utils_pr_service = UtilsPRService()
purchase_return_repository = PurchaseReturnRepository()


class DeletePurchaseReturnService:
    async def delete_purchase_return(self, session: AsyncSession, purchase_return_id: str):
        pr = await utils_pr_service.validate_draft_status(session, purchase_return_id)

        if pr.shipped_date:
            PurchaseReturnException.cant_delete_shipped_return()

        if pr.status != 'draft':
            PurchaseReturnException.only_delete_when_draft()

        success = await purchase_return_repository.delete_purchase_return(
            purchase_return_id=purchase_return_id,
            session=session
        )
        if not success:
            PurchaseReturnException.error_while_delete_pr()




