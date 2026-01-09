from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime
from starlette.requests import Request

from src.celery_tasks.send_return_completion_notification import send_return_completion_notification_task
from src.crud.cash.repositories import CashRepository
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
from sqlmodel import and_, case
from src.errors.payment import PaymentException
from src.errors.return_order import ReturnOrderException
from src.schemas.order import PaymentStatusOrderType
from src.schemas.payment_refund import PaymentRefundStatusType
import logging
from src.schemas.return_order import ReturnOrderStatus
from decimal import Decimal

logger = logging.getLogger(__name__)

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()
user_repository = UserRepository()
cash_repository = CashRepository()

class CompleteReturnOrderService:
    async def complete_return(self, return_order_id: str, restore_stock: bool, request: Optional[Request], session: AsyncSession):
        return_order = await self.fetch_and_validate_return_order(return_order_id, session)

        now = datetime.now()
        refund_result = None

        try:
            await self.update_return_order_status(return_order_id, now, session)

            if restore_stock:
                await self.restore_product_stock(return_order.return_items, session)
                logger.info(f"Stock restored for return order {return_order_id}")

            if return_order.order.payment_method == "vnpay":
                client_ip = get_client_ip(request) if request else "127.0.0.1"
                refund_result = await self.process_vnpay_refund(return_order, session, client_ip)

                if refund_result["status"] == "failed":
                    await session.rollback()
                    ReturnOrderException.refund_failed()

            await order_repository.update_order_some_field(
                and_(Order.id == return_order.order_id),
                {
                    "status": "returned",
                    "updated_at": datetime.now()
                },
                session
            )

            await session.commit()

            try:
                send_return_completion_notification_task.delay(
                    return_order_id=return_order_id,
                    user_id=str(return_order.user_id),
                    order_code=return_order.order.code,
                    order_id=str(return_order.order_id),
                    stock_restored=restore_stock,
                    refund_success=refund_result.get("status") == "success" if refund_result else False
                )
                logger.info(f"Queued completion notification for return order {return_order_id}")
            except Exception as e:
                logger.error(f"Failed to queue notification task: {str(e)}")

            message = "Đã hoàn thành xử lý hoàn trả"
            if refund_result:
                if refund_result["status"] == "success":
                    message += " và hoàn tiền thành công"
                elif refund_result["status"] == "failed":
                    message += " nhưng hoàn tiền thất bại"

            return message, {
                "return_order_id": return_order_id,
                "stock_restored": restore_stock,
                "refund_processed": return_order.order.payment_method == "vnpay",
                "refund_result": refund_result,
                "completed_at": now.isoformat()
            }

        except Exception as e:
            await session.rollback()
            logger.error(f"Error completing return order {return_order_id}: {str(e)}")
            ReturnOrderException.error_return_order()


    async def fetch_and_validate_return_order(self, return_order_id: str, session: AsyncSession):
        conditions = [
            ReturnOrder.id == return_order_id,
            ReturnOrder.deleted_at.is_(None)
        ]
        options = [
            selectinload(ReturnOrder.return_items).selectinload(ReturnItem.order_detail),
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.user)
        ]
        return_order = await return_order_repository.get_return_order(session=session, where_conditions=conditions,
                                                                      options=options, for_update=True)

        if not return_order:
            ReturnOrderException.return_doesnt_exist()

        if return_order.status != ReturnOrderStatus.APPROVED:
            ReturnOrderException.must_be_approved_to_complete(return_order.status)

        if return_order.status == ReturnOrderStatus.COMPLETED:
            ReturnOrderException.already_completed()

        return return_order


    async def update_return_order_status(self, return_order_id: str, completed_at: datetime, session: AsyncSession):
        update_data = {
            "status": ReturnOrderStatus.COMPLETED,
            "refunded_at": completed_at,
            "updated_at": completed_at
        }

        await return_order_repository.update_return_order(
            and_(ReturnOrder.id == return_order_id),
            update_data,
            session
        )


    async def restore_product_stock(self, return_items: List[ReturnItem], session: AsyncSession):
        if not return_items:
            return

        order_detail_ids = [item.order_detail_id for item in return_items]
        conditions = [
            Order_Detail.id.in_(order_detail_ids),
            Order_Detail.deleted_at.is_(None)
        ]
        order_details, _ = await order_detail_repository.get_all_order_detail(session=session, where_conditions=conditions)

        order_detail_map = {str(od.id): od for od in order_details}

        variant_updates = []
        for return_item in return_items:
            order_detail = order_detail_map.get(str(return_item.order_detail_id))

            if not order_detail:
                logger.warning(f"Order detail {return_item.order_detail_id} not found")
                continue

            if not order_detail.product_variant_id:
                logger.warning(f"Order detail {return_item.order_detail_id} has no variant")
                continue

            variant_updates.append({
                "variant_id": order_detail.product_variant_id,
                "quantity_to_add": return_item.quantity
            })

        if variant_updates:
            await self.batch_update_variant_stock(variant_updates, session)
            logger.info(f"Updated stock for {len(variant_updates)} variants")


    async def batch_update_variant_stock(self, variant_updates: List[Dict], session: AsyncSession):
        if not variant_updates:
            return

        variant_ids = [update["variant_id"] for update in variant_updates]

        quantity_case = case(
            {
                update["variant_id"]: Product_Variant.quantity + update["quantity_to_add"]
                for update in variant_updates
            },
            value=Product_Variant.id
        )

        conditions = and_(
            Product_Variant.id.in_(variant_ids),
            Product_Variant.deleted_at.is_(None)
        )
        await product_variant_repository.update_product_variant({"quantity": quantity_case}, conditions, session)


    async def process_vnpay_refund(self, return_order: ReturnOrder, session: AsyncSession, client_ip: str) -> Dict[str, Any]:
        total_refund = sum(
            Decimal(str(item.refund_amount)) for item in return_order.return_items
        )

        conditions = [
            Payment.order_id == return_order.order_id,
            Payment.status == "success",
            Payment.deleted_at.is_(None)
        ]
        payment = await vnpay_repository.get_payment(session=session, where_conditions=conditions)

        if not payment:
            logger.error(f"Payment not found for order {return_order.order_id}")
            PaymentException.payment_not_found()

        refund_type = "03" if total_refund < payment.amount else "02"

        refund = await self.get_or_create_refund(payment.id, refund_type, total_refund, return_order.reason, session)

        refund.attempt_count += 1
        await session.flush()

        trans_date = (
            payment.pay_date.strftime("%Y%m%d%H%M%S")
            if payment.pay_date
            else payment.created_at.strftime("%Y%m%d%H%M%S")
        )

        refund_response = await payment_refund_service.refund_transaction(
            TransactionType=refund_type,
            order_id=str(return_order.order.code),
            amount=str(int(total_refund)),
            order_desc=f"Return refund for order {return_order.order.code}",
            trans_date=trans_date,
            ipaddr=client_ip or "127.0.0.1",
            transaction_no=payment.transaction_no,
        )

        return await self.process_refund_response(
            refund, refund_response, payment, return_order, total_refund, session
        )


    async def get_or_create_refund(self, payment_id: str, refund_type: str, total_refund: int, reason: str,
                                   session: AsyncSession) -> PaymentRefund:
        existing_refund = await payment_refund_repository.get_payment_refund(
            and_(
                PaymentRefund.payment_id == payment_id,
                PaymentRefund.deleted_at.is_(None)
            ),
            session
        )

        if existing_refund:
            return existing_refund

        refund = PaymentRefund(
            payment_id=payment_id,
            refund_type=refund_type,
            refund_amount=total_refund,
            refund_reason=f"Return order refund: {reason}",
            status=PaymentRefundStatusType.PENDING,
            created_at=datetime.now(),
            attempt_count=0
        )
        session.add(refund)
        await session.flush()
        return refund


    async def process_refund_response(self, refund: PaymentRefund, refund_response: Dict[str, Any], payment: Payment,
                                      return_order: ReturnOrder, total_refund: int, session: AsyncSession):
        response_code = refund_response.get("vnp_ResponseCode")
        vnp_txn_ref = refund_response.get("vnp_TxnRef")
        vnp_amount = int(refund_response.get("vnp_Amount", 0))

        refund.response_code = response_code
        refund.txn_ref = vnp_txn_ref
        refund.bank_code = refund_response.get("vnp_BankCode")
        refund.transaction_status = refund_response.get("vnp_TransactionStatus")

        is_success = (
                response_code == "00" and
                vnp_txn_ref == payment.txn_ref and
                vnp_amount == int(total_refund)
        )

        if is_success:
            refund.status = PaymentRefundStatusType.SUCCESS
            refund.transaction_no = refund_response.get("vnp_TransactionNo")

            await order_repository.update_order_some_field(
                and_(Order.id == return_order.order_id),
                {
                    "payment_status": PaymentStatusOrderType.REFUNDED,
                    "updated_at": datetime.now()
                },
                session
            )

            cash_transaction = await self.create_refund_cash_transaction(return_order, total_refund, session)

            await session.flush()

            return {
                "status": "success",
                "refund_id": str(refund.id),
                "amount": float(total_refund),
                "transaction_no": refund.transaction_no,
                "cash_transaction": {
                    "id": str(cash_transaction.id),
                    "transaction_code": cash_transaction.transaction_code,
                    "amount": float(cash_transaction.amount),
                    "transaction_date": cash_transaction.transaction_date.isoformat()
                }
            }

        else:
            refund.status = PaymentRefundStatusType.FAILED
            await session.flush()

            logger.warning(
                f"Refund failed for return order {return_order.id}. "
                f"Response code: {response_code}, Amount mismatch: {vnp_amount} != {int(total_refund)}"
            )

            return {
                "status": "failed",
                "refund_id": str(refund.id),
                "amount": float(total_refund),
                "response_code": response_code
            }


    async def create_refund_cash_transaction(self, return_order: ReturnOrder, refund_amount: int, session: AsyncSession) -> Any:
        user = return_order.user

        conditions = [
            User.id == return_order.user_id,
            User.deleted_at.is_(None)
        ]
        if not user:
            user = await user_repository.get_user(session=session, where_conditions=conditions)

        reference_name = f"{user.first_name} {user.last_name}" if user else "Unknown Customer"
        transaction_code = f"RF{int(datetime.now().timestamp() * 1000)}"

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
            'notes': f"Hoàn tiền đơn hàng {return_order.order.code} - Return #{return_order.id}",
            'performed_by': None
        }

        return await cash_repository.create_cash_transaction(transaction_data, session)









































