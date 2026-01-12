from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.purchase_return.services.utils_service import UtilsPRService
from src.errors.purchase_return import PurchaseReturnException
import logging

logger = logging.getLogger(__name__)

utils_pr_service = UtilsPRService()
purchase_return_repository = PurchaseReturnRepository()


class DeletePurchaseReturnService:
    async def delete_purchase_return(self, session: AsyncSession, purchase_return_id: str):
        pr = await self.validate_and_get_pr(session, purchase_return_id)
        try:
            pr.deleted_at = datetime.now()
            pr.updated_at = datetime.now()

            session.add(pr)
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            logger.error("Error delete purchase return: ", e)
            PurchaseReturnException.error_while_delete_pr()
            
            
    async def validate_and_get_pr(self, session: AsyncSession, purchase_return_id: str):
        pr = await utils_pr_service.validate_and_get_pr(
            session, 
            purchase_return_id,
            minimal=True
        )
        
        if pr.status != 'draft':
            PurchaseReturnException.only_delete_when_draft()
            
        if pr.shipped_date:
            PurchaseReturnException.cant_delete_shipped_return()
            
        if pr.approved_at:
            PurchaseReturnException.cant_delete_approved_return()
            
        return pr




