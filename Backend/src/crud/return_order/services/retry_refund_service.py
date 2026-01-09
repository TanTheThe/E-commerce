from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request
from src.celery_tasks.return_order_tasks import retry_failed_refund_task
from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.return_order.services.complete_return_order import CompleteReturnOrderService
from src.crud.vnpay.repositories import VNPayRepository
from src.crud.vnpay.utils import get_client_ip
from src.database.models import PaymentRefund, Payment, ReturnOrder, Order
from src.errors.payment import PaymentException
from src.errors.return_order import ReturnOrderException
from src.schemas.order import PaymentStatusOrderType
from src.schemas.payment_refund import PaymentRefundStatusType
from src.schemas.return_order import RefundRetrySource
import logging


payment_refund_repository = PaymentRefundRepository()
vnpay_repository = VNPayRepository()
return_order_repository = ReturnOrderRepository()
payment_refund_service = PaymentRefundService()
order_repository = OrderRepository()
complete_return_order_service = CompleteReturnOrderService()

logger = logging.getLogger(__name__)

class RetryRefundService:
    MAX_AUTO_RETRY_ATTEMPTS = 5     # Constant cho max attempts
    MAX_MANUAL_RETRY_ATTEMPTS = 10  # Manual có thể retry nhiều hơn

    async def retry_refund_payment(self, refund_id: str, request: Optional[Request], session: AsyncSession,
                                   source: RefundRetrySource = RefundRetrySource.MANUAL):

        refund = await payment_refund_repository.get_payment_refund(
            and_(PaymentRefund.id == refund_id, PaymentRefund.deleted_at.is_(None)),
            session,
            for_update=True
        )

        if not refund:
            PaymentException.payment_refund_not_found()

        if refund.status not in ["failed", "pending"]:
            PaymentException.cant_retry_refund_with_status(refund.status)

        max_attempts = (
            self.MAX_MANUAL_RETRY_ATTEMPTS if source == RefundRetrySource.MANUAL
            else self.MAX_AUTO_RETRY_ATTEMPTS
        )

        if refund.attempt_count >= max_attempts:
            ReturnOrderException.max_retry_attempts_reached(max_attempts)

        payment, return_order = await self.fetch_related_records(refund.payment_id, session)

        try:
            refund.attempt_count += 1

            trans_date = (
                payment.pay_date.strftime("%Y%m%d%H%M%S")
                if payment.pay_date
                else payment.created_at.strftime("%Y%m%d%H%M%S")
            )

            client_ip = get_client_ip(request) if request else "127.0.0.1"

            refund_response = await payment_refund_service.refund_transaction(
                TransactionType=refund.refund_type,
                order_id=str(return_order.order.code),
                amount=str(refund.refund_amount),
                order_desc=refund.refund_reason,
                trans_date=trans_date,
                ipaddr=client_ip,
                transaction_no=payment.transaction_no,
            )

            result = await self.process_refund_response(
                refund, refund_response, payment, return_order, source, session
            )

            await session.commit()

            if (result["status"] == "failed" and source == RefundRetrySource.AUTO and
                    refund.attempt_count < self.MAX_AUTO_RETRY_ATTEMPTS):
                await self.schedule_next_retry(refund_id, session)

            return result

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during refund retry {refund_id}: {str(e)}", exc_info=True)

            if refund.attempt_count >= self.MAX_AUTO_RETRY_ATTEMPTS:
                refund.status = PaymentRefundStatusType.MANUAL_REQUIRED
            else:
                refund.status = PaymentRefundStatusType.FAILED

            await session.commit()

            return {
                "status": "failed" if refund.attempt_count < self.MAX_AUTO_RETRY_ATTEMPTS else "manual_required",
                "message": f"Lỗi khi hoàn tiền: {str(e)}",
                "refund_id": refund_id,
                "attempt_count": refund.attempt_count,
                "show_manual_button": refund.attempt_count >= self.MAX_AUTO_RETRY_ATTEMPTS,
                "error": str(e) if source == RefundRetrySource.MANUAL else None
            }


    async def fetch_related_records(self, payment_id: str, session: AsyncSession) -> tuple[Payment, ReturnOrder]:
        conditions = [Payment.id == payment_id, Payment.deleted_at.is_(None)]
        payment = await vnpay_repository.get_payment(session=session, where_conditions=conditions)

        if not payment:
            PaymentException.payment_not_found()

        conditions = [
            ReturnOrder.order_id == payment.order_id,
            ReturnOrder.deleted_at.is_(None)
        ]
        options = [
            selectinload(ReturnOrder.return_items),
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.user)
        ]

        return_order = await return_order_repository.get_return_order(session=session, where_conditions=conditions,
                                                                      options=options)

        if not return_order:
            ReturnOrderException.return_doesnt_exist()

        return payment, return_order


    async def process_refund_response(self, refund: PaymentRefund, refund_response: Dict[str, Any], payment: Payment,
                                      return_order: ReturnOrder, source: RefundRetrySource, session: AsyncSession):
        response_code = str(refund_response.get("vnp_ResponseCode"))
        vnp_txn_ref = refund_response.get("vnp_TxnRef")
        vnp_amount = int(refund_response.get("vnp_Amount", 0))

        refund.response_code = response_code
        refund.txn_ref = vnp_txn_ref
        refund.bank_code = refund_response.get("vnp_BankCode")
        refund.transaction_status = refund_response.get("vnp_TransactionStatus")

        is_success = (
                response_code == "00" and
                vnp_txn_ref == payment.txn_ref and
                vnp_amount == int(refund.refund_amount)
        )

        if is_success:
            return await self.handle_refund_success(
                refund, refund_response, payment, return_order, session
            )
        else:
            return await self.handle_refund_failure(
                refund, response_code, source, session
            )

    async def handle_refund_success(self, refund: PaymentRefund, refund_response: Dict[str, Any], payment: Payment,
                                    return_order: ReturnOrder, session: AsyncSession) -> Dict[str, Any]:

        refund.status = PaymentRefundStatusType.SUCCESS
        refund.transaction_no = refund_response.get("vnp_TransactionNo")
        refund.success_at = datetime.now()

        await order_repository.update_order_some_field(
            and_(Order.id == return_order.order_id),
            {
                "payment_status": PaymentStatusOrderType.REFUNDED,
                "updated_at": datetime.now()
            },
            session
        )

        cash_transaction = await complete_return_order_service.create_refund_cash_transaction(
            return_order=return_order,
            refund_amount=refund.refund_amount,
            session=session
        )

        await session.flush()

        return {
            "status": "success",
            "message": "Hoàn tiền thành công",
            "refund_id": str(refund.id),
            "attempt_count": refund.attempt_count,
            "show_manual_button": False,
            "cash_transaction": {
                "id": str(cash_transaction.id),
                "transaction_code": cash_transaction.transaction_code,
                "amount": float(cash_transaction.amount),
                "transaction_date": cash_transaction.transaction_date.isoformat()
            }
        }

    async def handle_refund_failure(self, refund: PaymentRefund, response_code: str, source: RefundRetrySource,
                                    session: AsyncSession) -> Dict[str, Any]:
        max_attempts = (
            self.MAX_MANUAL_RETRY_ATTEMPTS if source == RefundRetrySource.MANUAL
            else self.MAX_AUTO_RETRY_ATTEMPTS
        )

        if refund.attempt_count >= max_attempts:
            refund.status = PaymentRefundStatusType.MANUAL_REQUIRED
            message = f"Hoàn tiền thất bại {max_attempts} lần, cần xử lý thủ công"
            status_result = "manual_required"
        else:
            refund.status = PaymentRefundStatusType.FAILED
            message = f"Hoàn tiền thất bại (lần {refund.attempt_count}/{max_attempts})"
            status_result = "failed"

        await session.flush()

        logger.warning(
            f"Refund {refund.id} failed on attempt #{refund.attempt_count} "
            f"(response_code: {response_code})"
        )

        next_retry_in = None
        if source == RefundRetrySource.AUTO and refund.attempt_count < max_attempts:
            # Exponential backoff: 1h, 2h, 4h, 8h, 16h
            next_retry_in = 3600 * (2 ** (refund.attempt_count - 1))

        return {
            "status": status_result,
            "message": message,
            "refund_id": str(refund.id),
            "attempt_count": refund.attempt_count,
            "show_manual_button": refund.attempt_count >= max_attempts,
            "response_code": response_code,
            "next_auto_retry_in": next_retry_in
        }


    async def schedule_next_retry(self, refund_id: str, session: AsyncSession):
        refund = await payment_refund_repository.get_payment_refund(
            and_(PaymentRefund.id == refund_id),
            session
        )

        countdown = 3600 * (2 ** (refund.attempt_count - 1))

        try:
            retry_failed_refund_task.apply_async(
                args=[refund_id],
                countdown=countdown
            )
            logger.info(
                f"Scheduled next auto retry for refund {refund_id} "
                f"in {countdown}s (attempt #{refund.attempt_count + 1})"
            )
        except Exception as e:
            logger.error(f"Failed to schedule next retry: {str(e)}")




