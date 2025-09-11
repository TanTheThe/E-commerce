from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import PaymentRefund

class PaymentRefundRepository:
    async def create_refund(self, refund_dict: dict, session: AsyncSession):
        refund = PaymentRefund(**refund_dict)
        session.add(refund)

        return refund