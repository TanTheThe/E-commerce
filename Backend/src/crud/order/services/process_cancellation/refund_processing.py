from datetime import datetime
from fastapi import Request
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.crud.vnpay.utils import get_client_ip
from src.database.models import Order, Payment, PaymentRefund
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.order import PaymentStatusOrderType
from src.schemas.vnpay import PaymentStatusType
from src.schemas.payment_refund import PaymentRefundStatusType

vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()


class RefundProcessingService:
    async def process_refund_if_paid(self, session: AsyncSession, order: Order, request: Request):
        if order.payment_status != PaymentStatusOrderType.SUCCESS:
            return False

        condition_payment = [Payment.order_id == order.id, Payment.status == PaymentStatusType.SUCCESS]
        payment = await vnpay_repository.get_payment(session=session, where_conditions=condition_payment)

        if not payment:
            return False

        refund = PaymentRefund(
            payment_id=payment.id,
            refund_type="02",  # Full refund
            refund_amount=payment.amount,
            refund_reason="Order cancelled",
            status=PaymentRefundStatusType.PENDING,
            created_at=datetime.now(),
        )

        session.add(refund)
        await session.flush()

        refund_response = await payment_refund_service.refund_transaction(
            TransactionType="02",
            order_id=str(order.code),
            amount=str(payment.amount * 100),  # VNPAY expects amount * 100
            order_desc=f"Refund for order {order.code}",
            trans_date=payment.pay_date.strftime("%Y%m%d%H%M%S") if payment.pay_date else payment.created_at.strftime("%Y%m%d%H%M%S"),
            ipaddr=get_client_ip(request),
            transaction_no=payment.transaction_no,
        )

        if refund_response.get("vnp_ResponseCode") == "00" and refund_response.get("vnp_TxnRef") == payment.txn_ref:
            refund.status = PaymentRefundStatusType.SUCCESS
            refund.transaction_no = refund_response.get("vnp_TransactionNo")
            refund.response_code = refund_response.get("vnp_ResponseCode")
            refund.txn_ref = refund_response.get("vnp_TxnRef")
            refund.bank_code = refund_response.get("vnp_BankCode")
            refund.transaction_status = refund_response.get("vnp_TransactionStatus")

            order.payment_status = PaymentStatusOrderType.REFUNDED
        else:
            refund.status = PaymentRefundStatusType.FAILED
            refund.response_code = refund_response.get("vnp_ResponseCode")

        session.add(refund)
        session.add(order)

        return refund.status == PaymentRefundStatusType.SUCCESS

