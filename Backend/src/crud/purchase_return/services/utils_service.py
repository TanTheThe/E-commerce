from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.database.models import PurchaseReturn
from src.errors.purchase_return import PurchaseReturnException

purchase_return_repository = PurchaseReturnRepository()

class UtilsPRService:
    async def validate_and_get_pr(self, session: AsyncSession, purchase_return_id: str):
        condition = [PurchaseReturn.id == purchase_return_id]
        options = [
            selectinload(PurchaseReturn.purchase_order),
            selectinload(PurchaseReturn.goods_receipt),
            selectinload(PurchaseReturn.supplier),
            selectinload(PurchaseReturn.warehouse),
            selectinload(PurchaseReturn.return_details)
        ]

        pr = await purchase_return_repository.get_purchase_return(
            session=session,
            where_conditions=condition,
            options=options
        )

        if not pr:
            PurchaseReturnException.pr_not_found()

        return pr
