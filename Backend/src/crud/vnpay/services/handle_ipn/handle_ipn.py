from sqlmodel.ext.asyncio.session import AsyncSession
from src.config import Config
from src.crud.vnpay.services.handle_ipn.payment_processing import PaymentProcessingService
from src.crud.vnpay.services.handle_ipn.vnpay_validation import VNPayValidationService
import logging

logger = logging.getLogger(__name__)

validation_service = VNPayValidationService()
payment_processing_service = PaymentProcessingService()


class HandleIPNService:
    async def handle_ipn(self, input_data: dict, session: AsyncSession):
        if not input_data:
            return {"RspCode": "99", "Message": "Invalid request"}

        if not validation_service.validate_signature(Config.VNPAY_HASH_SECRET_KEY, input_data):
            return {"RspCode": "97", "Message": "Invalid Signature"}

        if not validation_service.validate_transaction_time(input_data.get("vnp_PayDate", "")):
            return {"RspCode": "99", "Message": "Invalid transaction time"}

        try:
            await payment_processing_service.process_payment(input_data, session)

            vnp_response_code = input_data.get("vnp_ResponseCode")
            if vnp_response_code == "00":
                return {"RspCode": "00", "Message": "Confirm Success"}
            else:
                return {"RspCode": "00", "Message": "Payment Error"}

        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}", exc_info=True)
            await session.rollback()
            return {"RspCode": "99", "Message": "Internal error"}


