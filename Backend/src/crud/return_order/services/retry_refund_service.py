from fastapi import HTTPException
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request
from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.crud.vnpay.utils import get_client_ip
from src.database.models import PaymentRefund, Payment, ReturnOrder, Order
from src.errors.payment import PaymentException
from src.schemas.order import PaymentStatusOrderType
from src.schemas.payment_refund import PaymentRefundStatusType

payment_refund_repository = PaymentRefundRepository()
vnpay_repository = VNPayRepository()
return_order_repository = ReturnOrderRepository()
payment_refund_service = PaymentRefundService()
order_repository = OrderRepository()

class RetryRefundService:
    async def retry_refund_payment(self, refund_id: str, request: Request, session: AsyncSession):
        refund = await payment_refund_repository.get_payment_refund(
            and_(PaymentRefund.id == refund_id),
            session
        )

        if not refund:
            PaymentException.payment_refund_not_found()

        if refund.status not in ["failed", "pending"]:
            raise HTTPException(status_code=400, detail="Chỉ có thể retry refund có status failed hoặc pending")

        payment = await vnpay_repository.get_payment(
            and_(Payment.id == refund.payment_id),
            session
        )

        conditions = [ReturnOrder.order_id == payment.order_id]
        return_order = await return_order_repository.get_return_order(conditions, session)

        try:
            refund.attempt_count += 1
            refund_response = await payment_refund_service.refund_transaction(
                TransactionType=refund.refund_type,
                order_id=str(return_order.order.code),
                amount=str(refund.refund_amount),
                order_desc=refund.refund_reason,
                trans_date=payment.pay_date.strftime(
                    "%Y%m%d%H%M%S") if payment.pay_date else payment.created_at.strftime("%Y%m%d%H%M%S"),
                ipaddr=get_client_ip(request),
                transaction_no=payment.transaction_no,
            )

            vnp_amount = int(refund_response.get("vnp_Amount")) * 100

            if (refund_response.get("vnp_ResponseCode") == "00" and
                    refund_response.get("vnp_TxnRef") == payment.txn_ref and
                    vnp_amount == refund.refund_amount):

                refund.status = PaymentRefundStatusType.SUCCESS
                refund.transaction_no = refund_response.get("vnp_TransactionNo")
                refund.response_code = refund_response.get("vnp_ResponseCode")
                refund.txn_ref = refund_response.get("vnp_TxnRef")
                refund.bank_code = refund_response.get("vnp_BankCode")
                refund.transaction_status = refund_response.get("vnp_TransactionStatus")

                await order_repository.update_order_some_field(
                    and_(Order.id == return_order.order_id),
                    {"payment_status": PaymentStatusOrderType.REFUNDED},
                    session
                )
                await session.commit()

                return {
                    "status": "success",
                    "message": "Hoàn tiền thành công",
                    "refund_id": refund_id,
                    "attempt_count": refund.attempt_count
                }

            else:
                if refund.attempt_count >= 5:
                    refund.status = PaymentRefundStatusType.MANUAL_REQUIRED
                    await session.commit()

                    return {
                        "status": "manual_required",
                        "message": "Hoàn tiền thất bại 5 lần, cần xử lý thủ công",
                        "refund_id": refund_id,
                        "attempt_count": refund.attempt_count,
                        "show_manual_button": True
                    }
                else:
                    refund.status = PaymentRefundStatusType.FAILED
                    refund.response_code = refund_response.get("vnp_ResponseCode")
                    await session.commit()

                    return {
                        "status": "failed",
                        "message": f"Hoàn tiền thất bại (lần {refund.attempt_count}/5)",
                        "refund_id": refund_id,
                        "attempt_count": refund.attempt_count,
                        "show_manual_button": refund.attempt_count >= 5
                    }

        except Exception as e:
            if refund.attempt_count >= 5:
                refund.status = PaymentRefundStatusType.MANUAL_REQUIRED
            else:
                refund.status = PaymentRefundStatusType.FAILED

            await session.commit()

            return {
                "status": "failed" if refund.attempt_count < 5 else "manual_required",
                "message": f"Lỗi khi hoàn tiền (lần {refund.attempt_count}/5)",
                "refund_id": refund_id,
                "attempt_count": refund.attempt_count,
                "show_manual_button": refund.attempt_count >= 5
            }