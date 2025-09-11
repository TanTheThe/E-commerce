from datetime import datetime
from typing import Tuple, Optional
from sqlalchemy.orm import selectinload
from fastapi import Request
from src.crud.notification.services import NotificationService
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.crud.vnpay.utils import get_client_ip
from src.database.models import Order, Payment, PaymentRefund, Order_Detail, Product_Variant, Product, Special_Offer, \
    UserSpecialOffer
from src.crud.address.repositories import AddressRepository
from src.crud.order.repositories import OrderRepository
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.user.repositories import UserRepository
from src.crud.product.repositories import ProductRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.color.repositories import ColorRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, func, or_, asc, desc, update, select
from src.errors.order import OrderException
from src.schemas.order import CancelOrderRequest, ProcessCancellationRequest

order_repository = OrderRepository()
special_offer_repository = SpecialOfferRepository()
user_repository = UserRepository()
address_repository = AddressRepository()
product_repository = ProductRepository()
order_detail_repository = OrderDetailRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
notification_service = NotificationService()

CANCELLATION_REASONS = {
    "change_mind": "Tôi đã thay đổi ý định",
    "wrong_product": "Đặt nhầm sản phẩm",
    "wrong_address": "Sai địa chỉ giao hàng",
    "payment_issue": "Vấn đề về thanh toán",
    "delivery_time": "Thời gian giao hàng không phù hợp",
    "found_better_price": "Tìm được giá tốt hơn ở nơi khác",
    "other": "Lý do khác"
}


class CancelOrderService:
    def get_final_cancellation_reason(self, reason_key: str, reason_detail: Optional[str] = None) -> str:
        if reason_key == "other":
            return reason_detail or "Lý do khác"
        return CANCELLATION_REASONS.get(reason_key, "Lý do không xác định")

    async def cancel_order_general(self, order_id: str, user_id: str, request: CancelOrderRequest,
                                   session: AsyncSession):
        conditions_order = and_(Order.id == order_id, Order.user_id == user_id, Order.deleted_at.is_(None))
        joins_order = [selectinload(Order.order_detail), selectinload(Order.payments)]
        order = await order_repository.get_order(conditions_order, session, joins_order)

        if not order:
            OrderException.not_found()

        can_cancel, reason = await self.can_cancel_order(order)
        if not can_cancel:
            OrderException.order_cant_cancelled()

        message = ""
        action_taken = ""
        final_reason = self.get_final_cancellation_reason(request.reason, request.reason_detail)

        try:
            if order.status == "pending":
                success = await self.cancel_order_directly(
                    session, order_id, final_reason
                )

                if success:
                    await notification_service.create_order_cancelled_notification(
                        session=session,
                        order_id=order_id,
                        customer_id=user_id,
                        order_code=order.code,
                        reason=final_reason
                    )

                    message = f"Đơn hàng #{order.code} đã được hủy thành công"
                    action_taken = "cancelled"
                else:
                    OrderException.error_cancelled()

            elif order.status == "confirmed":
                success = await self.request_cancellation(
                    session, order_id,
                    final_reason,
                    request.reason_detail
                )

                if success:
                    await notification_service.create_cancellation_request_notification(
                        session=session,
                        order_id=order_id,
                        customer_id=user_id,
                        order_code=order.code,
                        reason=final_reason,
                        reason_detail=request.reason_detail
                    )

                    message = f"Yêu cầu hủy đơn hàng #{order.code} đã được gửi. Vui lòng chờ admin xử lý."
                    action_taken = "request_sent"
                else:
                    OrderException.error_cancelled()

            await session.commit()

            return message, {
                "order_id": order_id,
                "order_code": order.code,
                "status": order.status,
                "action_taken": action_taken
            }

        except Exception as e:
            await session.rollback()
            OrderException.error_cancelled()



    async def can_cancel_order(self, order: Order) -> Tuple[bool, str]:
        if order.status == "cancelled":
            return False, "Đơn hàng đã được hủy trước đó"

        if order.status == "delivered":
            return False, "Không thể hủy đơn hàng đã hoàn thành"

        if order.status == "shipping":
            return False, "Không thể hủy đơn hàng đang giao"

        if order.status in ["pending", "confirmed"]:
            return True, "Có thể hủy đơn hàng"

        return False, f"Không thể hủy đơn hàng ở trạng thái {order.status}"

    async def cancel_order_directly(self, session: AsyncSession, order_id: str,
                                    reason: str = "Khách hàng yêu cầu hủy đơn hàng"):
        condition = and_(Order.id == order_id)
        await order_repository.update_order_some_field(condition, {
            "status": "cancelled",
            "cancellation_reason": reason,
            "cancellation_status": "approved",  # Auto approved for pending
            "cancellation_requested_at": datetime.now(),
            "updated_at": datetime.now()
        }, session)

        await self.restore_special_offer_usage(session, order_id)
        await self.restore_product_quantities(session, order_id)

        return True

    async def restore_special_offer_usage(self, session: AsyncSession, order_id: str):
        condition = and_(Order.id == order_id, Order.special_offer_id.isnot(None))
        order = await order_repository.get_order(condition, session)

        if order and order.special_offer_id:
            await special_offer_repository.update_offer_some_field(
                and_(Special_Offer.id == order.special_offer_id),
                {"used_quantity": Special_Offer.used_quantity - 1},
                session
            )

            await special_offer_repository.update_user_offer_some_field(
                and_(
                    UserSpecialOffer.special_offer_id == order.special_offer_id,
                    UserSpecialOffer.user_id == order.user_id
                ),
                {"used_at": None},
                session
            )

    async def restore_product_quantities(self, session: AsyncSession, order_id: str):
        condition = [Order_Detail.order_id == order_id, Order_Detail.deleted_at.is_(None)]
        order_details, _ = await order_detail_repository.get_all_order_detail(condition, session, skip=0, limit=1000)

        for detail in order_details:
            if detail.product_variant_id:
                await product_variant_repository.update_product_variant(
                    {"quantity": Product_Variant.quantity + detail.quantity},
                    and_(Product_Variant.id == detail.product_variant_id),
                    session
                )

            if detail.product_id:
                await product_repository.update_product_some_field(
                    and_(Product.id == detail.product_id),
                    {
                        "total_sold": Product.total_sold - detail.quantity,
                        "popularity_score": func.greatest(Product.popularity_score - 1, 0)
                    },
                    session
                )

    async def process_refund(self, session: AsyncSession, order: Order, request: Request):
        condition_payment = and_(Payment.order_id == order.id, Payment.status == "success")
        payment = await vnpay_repository.get_payment(condition_payment, session)

        if not payment:
            return False

        refund = PaymentRefund(
            payment_id=payment.id,
            refund_type="01",  # Full refund
            refund_amount=payment.amount,
            refund_reason="Order cancelled",
            status="pending"
        )

        session.add(refund)
        await session.flush()

        refund_response = await payment_refund_service.refund_transaction(
            TransactionType="02",
            order_id=str(order.id),
            amount=str(payment.amount * 100),  # VNPAY expects amount * 100
            order_desc=f"Refund for order {order.code}",
            trans_date=payment.created_at.strftime("%Y%m%d%H%M%S"),
            ipaddr=get_client_ip(request)
        )

        if refund_response.get("vnp_ResponseCode") == "00":
            refund.status = "success"
            refund.transaction_no = refund_response.get("vnp_TransactionNo")
            refund.response_code = refund_response.get("vnp_ResponseCode")

            order.payment_status = "refunded"
        else:
            refund.status = "failed"
            refund.response_code = refund_response.get("vnp_ResponseCode")

        session.add(refund)
        session.add(order)

        return True

    async def request_cancellation(self, session: AsyncSession, order_id: str, reason: str,
                                   reason_detail: Optional[str] = None):
        cancellation_reason = reason
        if reason_detail:
            cancellation_reason += f" - {reason_detail}"

        condition = and_(Order.id == order_id)
        await order_repository.update_order_some_field(condition, {
            "cancellation_reason": cancellation_reason,
            "cancellation_status": "requested",  # Auto approved for pending
            "cancellation_requested_at": datetime.now(),
            "updated_at": datetime.now()
        }, session)

        return True

    async def get_cancellation_requests(self, session: AsyncSession, skip: int = 0, limit: int = 20):
        condition = [Order.cancellation_status == "requested", Order.deleted_at.is_(None)]
        joins = [selectinload(Order.user), selectinload(Order.order_detail)]
        order_by = [desc(Order.cancellation_requested_at)]

        orders, total = await order_repository.get_all_order(condition, session, order_by, skip=skip, limit=limit,
                                                             joins=joins)

        return orders, total

    async def get_orders_by_status(self, session: AsyncSession, status: str, skip: int = 0, limit: int = 20):
        condition = [Order.status == status, Order.deleted_at.is_(None)]
        joins = [selectinload(Order.user), selectinload(Order.order_detail)]
        order_by = [desc(Order.created_at)]

        orders, total = await order_repository.get_all_order(condition, session, order_by, skip=skip, limit=limit,
                                                             joins=joins)

        return orders, total

    async def cancel_order_by_admin(self, session: AsyncSession, order_id: str, request: Request):
        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        joins = [
            selectinload(Order.order_detail),
            selectinload(Order.user),
            selectinload(Order.payments)
        ]
        order = await order_repository.get_order(condition, session, joins=joins)

        if not order:
            return False

        condition_update = and_(Order.id == order_id)
        await order_repository.update_order_some_field(condition_update, {
            "status": "cancelled",
            "cancellation_status": "approved",
            "updated_at": datetime.now()
        }, session)

        await self.restore_special_offer_usage(session, order_id)
        await self.restore_product_quantities(session, order_id)

        if order.payment_status == "success":
            await self.process_refund(session, order, request)

        return True

    async def reject_cancellation(self, session: AsyncSession, order_id: str, reject_reason: str):
        condition_get = and_(Order.id == order_id, Order.deleted_at.is_(None))
        order = await order_repository.get_order(condition_get, session)

        if not order:
            return False

        current_reason = Order.cancellation_reason or ""
        new_reason = f"{current_reason} | Rejected: {reject_reason}"

        condition = and_(Order.id == order_id)
        await order_repository.update_order_some_field(condition, {
            "cancellation_status": "rejected",
            "cancellation_reason": new_reason,
            "updated_at": datetime.now()
        }, session)

        return True

    async def process_cancellation_general(self, order_id: str, data: ProcessCancellationRequest, request: Request,
                                           session: AsyncSession):
        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        joins = [
            selectinload(Order.order_detail),
            selectinload(Order.user),
            selectinload(Order.payments)
        ]
        order = await order_repository.get_order(condition, session, joins=joins)

        if not order:
            OrderException.not_found()

        if order.cancellation_status != "requested":
            OrderException.not_request_cancelled()

        message = ""
        try:
            if data.action == "handle_cancellation":
                success = await self.cancel_order_by_admin(session, order_id, request)

                if success:
                    await notification_service.create_cancellation_approved_notification(
                        session=session,
                        order_id=order_id,
                        customer_id=str(order.user_id),
                        order_code=order.code,
                        admin_note=data.admin_note
                    )

                    message = f"Đã chấp thuận hủy đơn hàng #{order.code}"
                else:
                    OrderException.not_accept_cancelled()
            elif data.action == "reject":
                if not data.reject_reason:
                    OrderException.reason_reject_cancelled()

                success = await self.reject_cancellation(session, order_id, data.reject_reason)

                if success:
                    await notification_service.create_cancellation_rejected_notification(
                        session=session,
                        order_id=order_id,
                        customer_id=str(order.user_id),
                        order_code=order.code,
                        reject_reason=data.reject_reason
                    )

                    message = f"Đã từ chối hủy đơn hàng #{order.code}"
                else:
                    OrderException.not_accept_cancelled()
            else:
                OrderException.action_invalid()

            await session.commit()

            return message, {
                "order_id": order_id,
                "order_code": order.code,
                "action": data.action
            }

        except Exception as e:
            await session.rollback()
            OrderException.error_cancelled()

