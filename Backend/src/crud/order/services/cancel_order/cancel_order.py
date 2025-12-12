from datetime import datetime
from typing import Tuple, Optional
from sqlalchemy.orm import selectinload
from src.crud.order.services.cancel_order.cancellation_notification import CancelNotificationService
from src.crud.order.services.cancel_order.inventory_restoration import InventoryRestorationService
from src.database.models import Order
from src.crud.order.repositories import OrderRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.order import OrderException
from src.schemas.order import CancelOrderRequest, CancellationStatusType
import logging

logger = logging.getLogger(__name__)

order_repository = OrderRepository()

inventory_restoration_service = InventoryRestorationService()
cancellation_notification_service = CancelNotificationService()


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
    async def can_cancel_order(self, order: Order) -> Tuple[bool, str]:
        if order.status == "cancelled":
            return False, "Đơn hàng đã được hủy trước đó"

        if order.status in ["delivered", "received"]:
            return False, "Không thể hủy đơn hàng đã hoàn thành"

        if order.status == "shipping":
            return False, "Không thể hủy đơn hàng đang giao"

        if order.status in ["pending", "confirmed"]:
            return True, "Có thể hủy đơn hàng"

        return False, f"Không thể hủy đơn hàng ở trạng thái {order.status}"


    def get_final_cancellation_reason(self, reason_key: str, reason_detail: Optional[str] = None) -> str:
        if reason_key == "other":
            return reason_detail or "Lý do khác"
        return CANCELLATION_REASONS.get(reason_key, "Lý do không xác định")


    async def cancel_order_directly(self, session: AsyncSession, order_id: str,
                                    reason: str = "Khách hàng yêu cầu hủy đơn hàng"):
        condition = and_(Order.id == order_id)
        await order_repository.update_order_some_field(condition, {
            "status": "cancelled",
            "cancellation_reason": reason,
            "cancellation_status": CancellationStatusType.APPROVED,  # Auto approved for pending
            "cancellation_requested_at": datetime.now(),
            "updated_at": datetime.now()
        }, session)

        await inventory_restoration_service.restore_all(session=session, order_id=order_id)

        return True


    async def request_cancellation(self, session: AsyncSession, order_id: str, reason: str,
                                   reason_detail: Optional[str] = None):
        cancellation_reason = reason
        if reason_detail:
            cancellation_reason += f" - {reason_detail}"

        condition = and_(Order.id == order_id)
        await order_repository.update_order_some_field(condition, {
            "cancellation_reason": cancellation_reason,
            "cancellation_status": CancellationStatusType.REQUESTED,  # Auto approved for pending
            "cancellation_requested_at": datetime.now(),
            "updated_at": datetime.now()
        }, session)

        return True


    async def cancel_order_by_customer(self, order_id: str, user_id: str, request: CancelOrderRequest,
                                       session: AsyncSession):
        conditions_order = [
            Order.id == order_id,
            Order.user_id == user_id,
            Order.deleted_at.is_(None)
        ]
        options = [
            selectinload(Order.order_detail),
            selectinload(Order.user),
            selectinload(Order.payments)
        ]
        order = await order_repository.get_order(session=session, where_conditions=conditions_order, options=options)

        if not order:
            raise OrderException.not_found()

        if order.cancellation_status == CancellationStatusType.REQUESTED:
            OrderException.already_cancelled()

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
                    await cancellation_notification_service.notify_order_cancelled(
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
                    await cancellation_notification_service.notify_cancellation_requested(
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
            logger.error(f"Failed to cancel order")
            OrderException.error_cancelled()




