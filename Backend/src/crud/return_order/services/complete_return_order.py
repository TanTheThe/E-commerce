from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from starlette.requests import Request
from src.crud.cash.repositories import CashRepository
from src.crud.notification.services.services import NotificationService
from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.user.repositories import UserRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.crud.vnpay.utils import get_client_ip
from src.database.models import ReturnOrder, Order_Detail, ReturnItem, Product_Variant, Payment, PaymentRefund, Order, \
    User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.payment import PaymentException
from src.errors.return_order import ReturnOrderException
from src.schemas.order import PaymentStatusOrderType
from src.schemas.payment_refund import PaymentRefundStatusType
from src.schemas.return_order import ReturnOrderStatusType

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
notification_service = NotificationService()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()
user_repository = UserRepository()
cash_repository = CashRepository()

class CompleteReturnOrderService:
    async def complete_return(self, return_order_id: str, restore_stock: bool, request: Request, session: AsyncSession):
        conditions = [ReturnOrder.id == return_order_id, ReturnOrder.status == "approved"]
        joins = [
            selectinload(ReturnOrder.return_items),
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.user)
        ]

        return_order = await return_order_repository.get_return_order(conditions, session, joins)
        if not return_order:
            ReturnOrderException.return_doesnt_exist()

        # try:
        #
        #
        # except Exception as e:
        #     await session.rollback()
        #     ReturnOrderException.error_return_order()
        await return_order_repository.update_return_order(
            and_(ReturnOrder.id == return_order_id),
            {
                "status": ReturnOrderStatusType.COMPLETED,
                "refunded_at": datetime.now()
            },
            session
        )

        if restore_stock:
            await self.restore_product_stock(return_order.return_items, session)

        refund_result = None
        if return_order.order.payment_method == "vnpay":
            client_ip = get_client_ip(request)
            refund_result = await self.process_refund_single_attempt(
                return_order,
                session,
                ipaddr=client_ip
            )

        await order_repository.update_order_some_field(
            and_(Order.id == return_order.order_id),
            {"status": "returned"},
            session
        )

        await notification_service.create_return_completed_notification(
            session=session,
            return_order_id=return_order_id,
            customer_id=str(return_order.user_id),
            order_code=return_order.order.code,
            stock_restored=restore_stock,
            order_id=str(return_order.order_id),
        )

        await session.commit()

        message = "Đã hoàn thành xử lý hoàn trả"
        if refund_result and refund_result.get("status") == "success":
            message += " và hoàn tiền thành công"
        elif refund_result and refund_result.get("status") == "failed":
            message += " nhưng hoàn tiền thất bại"

        return message, {
            "stock_restored": restore_stock,
            "refund_result": refund_result
        }

    async def restore_product_stock(self, return_items: List[ReturnItem], session: AsyncSession):
        for return_item in return_items:
            condition = and_(Order_Detail.id == str(return_item.order_detail_id), Order_Detail.deleted_at.is_(None))
            order_detail = await order_detail_repository.get_order_detail(condition, session)

            if order_detail and order_detail.product_variant_id:
                await product_variant_repository.update_product_variant(
                    {"quantity": Product_Variant.quantity + return_item.quantity},
                    and_(Product_Variant.id == order_detail.product_variant_id),
                    session
                )

    async def process_refund_single_attempt(self, return_order: ReturnOrder, session: AsyncSession, ipaddr: Optional[str] = None):
        total_refund = sum(item.refund_amount for item in return_order.return_items)

        payment = await vnpay_repository.get_payment(
            and_(Payment.order_id == return_order.order_id, Payment.status == "success"),
            session
        )
        if not payment:
            PaymentException.payment_not_found()

        refund_type = "03" if total_refund < payment.amount else "02"

        existing_refund = await payment_refund_repository.get_payment_refund(
            and_(PaymentRefund.payment_id == payment.id),
            session
        )

        if existing_refund:
            refund = existing_refund
        else:
            refund = PaymentRefund(
                payment_id=payment.id,
                refund_type=refund_type,
                refund_amount=total_refund,
                refund_reason=f"Return order refund: {return_order.reason}",
                status=PaymentRefundStatusType.PENDING,
                created_at=datetime.now(),
                attempt_count=0
            )
            session.add(refund)
            await session.flush()

        try:
            refund.attempt_count += 1
            client_ip = ipaddr or "127.0.0.1"

            refund_response = await payment_refund_service.refund_transaction(
                TransactionType=refund_type,
                order_id=str(return_order.order.code),
                amount=str(total_refund),
                order_desc=f"Return refund for order {return_order.order.code}",
                trans_date=payment.pay_date.strftime(
                    "%Y%m%d%H%M%S") if payment.pay_date else payment.created_at.strftime("%Y%m%d%H%M%S"),
                ipaddr=client_ip,
                transaction_no=payment.transaction_no,
            )

            vnp_amount = int(refund_response.get("vnp_Amount"))

            if (refund_response.get("vnp_ResponseCode") == "00" and
                    refund_response.get("vnp_TxnRef") == payment.txn_ref and
                    vnp_amount == total_refund):

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

                cash_transaction = await self.create_refund_cash_transaction(
                    return_order=return_order,
                    refund_amount=total_refund,
                    session=session
                )

                await session.flush()

                return {
                    "status": "success",
                    "refund_id": str(refund.id),
                    "amount": total_refund,
                    "transaction_no": refund.transaction_no,
                    "cash_transaction": {
                        "id": str(cash_transaction.id),
                        "transaction_code": cash_transaction.transaction_code,
                        "amount": cash_transaction.amount,
                        "transaction_date": cash_transaction.transaction_date.isoformat()
                    }
                }

            else:
                refund.status = PaymentRefundStatusType.FAILED
                refund.response_code = refund_response.get("vnp_ResponseCode")
                await session.flush()

                return {
                    "status": "failed",
                    "refund_id": str(refund.id),
                    "amount": total_refund
                }

        except Exception as e:
            refund.status = PaymentRefundStatusType.FAILED
            await session.flush()

            return {
                "status": "failed",
                "refund_id": str(refund.id),
                "amount": total_refund
            }


    async def create_refund_cash_transaction(self, return_order: ReturnOrder, refund_amount: int, session: AsyncSession):
        user = return_order.user

        if not user:
            condition = and_(
                User.deleted_at.is_(None),
                User.id == return_order.user_id,
                User.customer_status == "active"
            )
            user = await user_repository.get_user(condition, session)

        reference_name = f"{user.first_name} {user.last_name}" if user else None

        transaction_code = f"CT{int(datetime.now().timestamp() * 1000)}"

        transaction_data = {
            'transaction_code': transaction_code,
            'transaction_type': 'outflow',
            'category': 'refund',
            'amount': refund_amount,
            'transaction_date': datetime.now(),
            'reference_type': 'customer',
            'reference_id': return_order.user_id,
            'reference_name': reference_name,
            'payment_method': 'bank_transfer',
            'notes': f"Hoàn tiền cho đơn hàng {return_order.order.code} - Return order #{return_order.id}",
            'performed_by': None
        }

        cash_transaction = await cash_repository.create_cash_transaction(
            transaction_data,
            session
        )

        return cash_transaction









































