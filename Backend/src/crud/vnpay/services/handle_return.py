from sqlmodel.ext.asyncio.session import AsyncSession
from src.config import Config
from src.crud.vnpay.services.handle_ipn.payment_processing import PaymentProcessingService
from src.crud.vnpay.services.handle_ipn.vnpay_validation import VNPayValidationService
import logging

logger = logging.getLogger(__name__)

payment_processing_service = PaymentProcessingService()
validation_service = VNPayValidationService()


class HandleReturnService:
    async def handle_return(self, input_data: dict, session: AsyncSession) -> dict:
        if not input_data:
            raise ValueError("Invalid request data")

        order_code = input_data.get("vnp_TxnRef")
        if not order_code:
            raise ValueError("Missing order code")

        if not validation_service.validate_signature(Config.VNPAY_HASH_SECRET_KEY, input_data):
            raise ValueError("Invalid signature")

        try:
            result = await payment_processing_service.process_payment(input_data, session)
            return result

        except Exception as e:
            logger.error(f"Return URL processing error: {str(e)}", exc_info=True)
            await session.rollback()
            raise



