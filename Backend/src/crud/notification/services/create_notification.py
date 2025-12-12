from datetime import datetime, timedelta
from typing import Optional
from src.crud.notification.repositories import NotificationRepository
from sqlmodel.ext.asyncio.session import AsyncSession
import json

from src.database.models import Notification
from src.errors.notification import NotificationException
from src.schemas.notification import RecipientType, NotificationType, ActionType
import logging

logger = logging.getLogger(__name__)

notification_repository = NotificationRepository()

class CreateNotificationService:
    async def check_duplicate_notification(self, session: AsyncSession,
                                            recipient_id: Optional[str],
                                            notification_type: str,
                                            order_id: Optional[str] = None,
                                            return_order_id: Optional[str] = None,
                                            time_threshold_minutes: int = 5) -> bool:
        time_threshold = datetime.now() - timedelta(minutes=time_threshold_minutes)

        conditions = [
            Notification.type == notification_type,
            Notification.created_at >= time_threshold
        ]

        if recipient_id:
            conditions.append(Notification.recipient_id == recipient_id)

        if order_id:
            conditions.append(Notification.order_id == order_id)

        if return_order_id:
            conditions.append(Notification.return_order_id == return_order_id)

        existing = await notification_repository.get_notification(session=session, where_conditions=conditions)
        return existing is not None


    # Gửi thông báo hủy đơn hàng khi đơn hàng ở trạng thái 'pending'
    async def create_order_cancelled_notification(self, session: AsyncSession, order_id: str, customer_id: str, order_code: str,
                                                  reason: str = "Khách hàng tự động hủy đơn hàng"):
        is_duplicate = await self.check_duplicate_notification(
            session=session,
            recipient_id=None,
            notification_type=NotificationType.ORDER_CANCELLED,
            order_id=order_id
        )

        if is_duplicate:
            NotificationException.order_cancellation_sent_recently()

        notification_data = {
            "recipient_type": RecipientType.ADMIN,
            "recipient_id": None,  # Admin không cần ID
            "sender_type": RecipientType.CUSTOMER,
            "sender_id": customer_id,
            "type": NotificationType.ORDER_CANCELLED,
            "title": f"Đơn hàng #{order_code} đã bị hủy",
            "message": f"Khách hàng đã hủy đơn hàng #{order_code}. Lý do: {reason}",
            "order_id": order_id,
            "action_type": None,  # Không cần action vì đã hủy rồi
            "action_data": None
        }

        return await notification_repository.create_notification(notification_data, session)

    # Gửi thông báo hủy đơn hàng khi đơn hàng ở trạng thái 'confirmed'
    async def create_cancellation_request_notification(self, session: AsyncSession, order_id: str, customer_id: str, order_code: str,
                                                  reason: str, reason_detail: Optional[str] = None):
        is_duplicate = await self.check_duplicate_notification(
            session=session,
            recipient_id=None,
            notification_type=NotificationType.ORDER_CANCELLATION_REQUEST,
            order_id=order_id
        )

        if is_duplicate:
            NotificationException.order_cancellation_sent_recently()

        action_data = {
            "order_id": order_id,
            "customer_id": customer_id,
            "reason": reason,
            "reason_detail": reason_detail,
            "requested_at": datetime.now().isoformat()
        }

        notification_data = {
            "recipient_type": RecipientType.ADMIN,
            "recipient_id": None,
            "sender_type": RecipientType.CUSTOMER,
            "sender_id": customer_id,
            "type": NotificationType.ORDER_CANCELLATION_REQUEST,
            "title": f"Yêu cầu hủy đơn hàng #{order_code}",
            "message": f"Khách hàng yêu cầu hủy đơn hàng #{order_code}. Lý do: {reason}" +
                       (f" - {reason_detail}" if reason_detail else ""),
            "order_id": order_id,
            "action_type": ActionType.HANDLE_CANCELLATION,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    # Gửi thông báo khi admin approve yêu cầu hủy đơn
    async def create_cancellation_approved_notification(self, session: AsyncSession, order_id: str, customer_id: str, order_code: str,
                                                        admin_id: Optional[str] = None, admin_note: Optional[str] = None):
        message = f"Yêu cầu hủy đơn hàng #{order_code} đã được chấp thuận."
        if admin_note:
            message += f" Ghi chú: {admin_note}"

        action_data = {
            "order_id": order_id,
            "approved_by": admin_id,
            "approved_at": datetime.now().isoformat(),
            "admin_note": admin_note
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": admin_id,
            "type": NotificationType.ORDER_CANCELLATION_APPROVED,
            "title": f"Đơn hàng #{order_code} đã được hủy",
            "message": message,
            "order_id": order_id,
            "action_type": None,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    # Gửi thông báo khi admin reject yêu cầu hủy đơn
    async def create_cancellation_rejected_notification(self, session: AsyncSession, order_id: str, customer_id: str, order_code: str,
                                                        reject_reason: str, admin_id: Optional[str] = None):
        action_data = {
            "order_id": order_id,
            "rejected_by": admin_id,
            "rejected_at": datetime.now().isoformat(),
            "reject_reason": reject_reason
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": admin_id,
            "type": NotificationType.ORDER_CANCELLATION_REJECTED,
            "title": f"Yêu cầu hủy đơn hàng #{order_code} bị từ chối",
            "message": f"Yêu cầu hủy đơn hàng #{order_code} không được chấp thuận. Lý do: {reject_reason}",
            "order_id": order_id,
            "action_type": None,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    async def create_assign_special_offer_notification(self, session: AsyncSession, special_offer_id: str, special_offer_name: str,
                                                       customer_id: str, admin_note: Optional[str] = None, admin_id: Optional[str] = None):
        message = f"Bạn vừa nhận được khuyến mãi #{special_offer_name} từ cửa hàng."
        if admin_note:
            message += f" Ghi chú: {admin_note}"

        action_data = {
            "special_offer_id": special_offer_id,
            "assigned_by": admin_id,
            "assigned_at": datetime.now().isoformat(),
            "admin_note": admin_note
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": admin_id,
            "type": NotificationType.SPECIAL_OFFER_ASSIGNED,
            "title": f"Vừa nhận được khuyến mãi #{special_offer_name}",
            "message": message,
            "special_offer_id": special_offer_id,
            "action_type": None,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    # Gửi thông báo hoàn trả đơn hàng
    async def create_return_request_notification(self, session: AsyncSession, return_order_id: str, customer_id: str, order_code: str, order_id: str):
        is_duplicate = await self.check_duplicate_notification(
            session=session,
            recipient_id=None,
            notification_type=NotificationType.RETURN_ORDER_REQUEST,
            return_order_id=return_order_id
        )

        if is_duplicate:
            NotificationException.return_order_sent_recently()

        action_data = {
            "return_order_id": return_order_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "requested_at": datetime.now().isoformat(),
            "status": "pending"
        }

        notification_data = {
            "recipient_type": RecipientType.ADMIN,
            "recipient_id": None,
            "sender_type": RecipientType.CUSTOMER,
            "sender_id": customer_id,
            "type": NotificationType.RETURN_ORDER_REQUEST,
            "title": f"Yêu cầu hoàn trả đơn hàng #{order_code}",
            "message": f"Khách hàng yêu cầu hoàn trả đơn hàng #{order_code}. Vui lòng kiểm tra và xử lý.",
            "order_id": order_id,
            "return_order_id": return_order_id,
            "action_type": ActionType.HANDLE_RETURN,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    async def create_return_approved_notification(self, session: AsyncSession, return_order_id: str, customer_id: str, order_code: str,
                                                  order_id: str, admin_note: Optional[str] = None, admin_id: Optional[str] = None):
        message = f"Yêu cầu hoàn trả đơn hàng #{order_code} đã được chấp thuận."
        if admin_note:
            message += f" Ghi chú: {admin_note}"

        action_data = {
            "return_order_id": return_order_id,
            "order_id": order_id,
            "approved_by": admin_id,
            "approved_at": datetime.now().isoformat(),
            "admin_note": admin_note
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": admin_id,
            "type": NotificationType.RETURN_ORDER_APPROVED,
            "title": f"Yêu cầu hoàn trả đơn hàng #{order_code} đã được chấp thuận",
            "message": message,
            "order_id": order_id,
            "return_order_id": return_order_id,
            "action_type": None,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    async def create_return_rejected_notification(self, session: AsyncSession, return_order_id: str, customer_id: str, order_code: str,
                                                        order_id: str, reject_reason: str, admin_id: Optional[str] = None):

        action_data = {
            "return_order_id": return_order_id,
            "order_id": order_id,
            "rejected_by": admin_id,
            "rejected_at": datetime.now().isoformat(),
            "reject_reason": reject_reason
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": admin_id,
            "type": NotificationType.RETURN_ORDER_REJECTED,
            "title": f"Yêu cầu hoàn trả đơn hàng #{order_code} bị từ chối",
            "message": f"Yêu cầu hoàn trả đơn hàng #{order_code} không được chấp thuận. Lý do: {reject_reason}",
            "order_id": order_id,
            "return_order_id": return_order_id,
            "action_type": None,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    async def create_return_completed_notification(self, session: AsyncSession, return_order_id: str, order_code: str,
                                                   customer_id: str, stock_restored: bool, order_id: str):
        if stock_restored:
            message = f"Yêu cầu hoàn trả đơn hàng #{order_code} đã được xử lý thành công. Sản phẩm đã được hoàn trả về kho và số tiền hoàn lại sẽ được xử lý trong thời gian sớm nhất."
            action_status = "completed_with_stock_restore"
        else:
            message = f"Yêu cầu hoàn trả đơn hàng #{order_code} đã được xử lý thành công. Số tiền hoàn lại sẽ được xử lý trong thời gian sớm nhất."
            action_status = "completed_without_stock_restore"

        action_data = {
            "return_order_id": return_order_id,
            "customer_id": customer_id,
            "stock_restored": stock_restored,
            "action_status": action_status,
            "completed_at": datetime.now().isoformat()
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": None,
            "type": NotificationType.RETURN_ORDER_COMPLETED,
            "title": f"Hoàn trả đơn hàng #{order_code} đã xử lý xong",
            "message": message,
            "order_id": order_id,
            "return_order_id": return_order_id,
            "action_type": None,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)


    async def create_order_confirmed_notification(self, session: AsyncSession, order_id: str, customer_id: str,
                                                  order_code: str, admin_id: Optional[str] = None,
                                                  note: Optional[str] = None):
        is_duplicate = await self.check_duplicate_notification(
            session=session,
            recipient_id=customer_id,
            notification_type=NotificationType.ORDER_CONFIRMED,
            order_id=order_id
        )

        if is_duplicate:
            return None

        message = f"Đơn hàng #{order_code} đã được xác nhận và đang được chuẩn bị."
        if note:
            message += f" Ghi chú: {note}"

        action_data = {
            "order_id": order_id,
            "confirmed_by": admin_id,
            "confirmed_at": datetime.now().isoformat(),
            "note": note
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": admin_id,
            "type": NotificationType.ORDER_CONFIRMED,
            "title": f"Đơn hàng #{order_code} đã được xác nhận",
            "message": message,
            "order_id": order_id,
            "action_type": ActionType.VIEW_ORDER,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)


    async def create_order_shipping_notification(self, session: AsyncSession, order_id: str, customer_id: str,
                                                 order_code: str, estimated_delivery: Optional[datetime] = None,
                                                 admin_id: Optional[str] = None, note: Optional[str] = None):
        is_duplicate = await self.check_duplicate_notification(
            session=session,
            recipient_id=customer_id,
            notification_type=NotificationType.ORDER_SHIPPING,
            order_id=order_id
        )

        if is_duplicate:
            return None

        message = f"Đơn hàng #{order_code} đang trên đường giao đến bạn."

        if estimated_delivery:
            delivery_str = estimated_delivery.strftime("%d/%m/%Y %H:%M")
            message += f" Dự kiến giao hàng: {delivery_str}."

        if note:
            message += f" Ghi chú: {note}"

        action_data = {
            "order_id": order_id,
            "shipping_started_by": admin_id,
            "shipping_started_at": datetime.now().isoformat(),
            "estimated_delivery": estimated_delivery.isoformat() if estimated_delivery else None,
            "note": note
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": admin_id,
            "type": NotificationType.ORDER_SHIPPING,
            "title": f"Đơn hàng #{order_code} đang được giao",
            "message": message,
            "order_id": order_id,
            "action_type": ActionType.TRACK_ORDER,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    async def create_order_delivered_notification(self, session: AsyncSession, order_id: str, customer_id: str,
                                                  order_code: str, admin_id: Optional[str] = None,
                                                  note: Optional[str] = None):

        is_duplicate = await self.check_duplicate_notification(
            session=session,
            recipient_id=customer_id,
            notification_type=NotificationType.ORDER_DELIVERED,
            order_id=order_id
        )

        if is_duplicate:
            return None

        message = f"Đơn hàng #{order_code} đã được giao thành công. Vui lòng kiểm tra và xác nhận đã nhận hàng."
        if note:
            message += f" Ghi chú: {note}"

        action_data = {
            "order_id": order_id,
            "delivered_by": admin_id,
            "delivered_at": datetime.now().isoformat(),
            "note": note,
            "requires_confirmation": True
        }

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": admin_id,
            "type": NotificationType.ORDER_DELIVERED,
            "title": f"Đơn hàng #{order_code} đã được giao",
            "message": message,
            "order_id": order_id,
            "action_type": ActionType.CONFIRM_RECEIVED,
            "action_data": json.dumps(action_data)
        }

        return await notification_repository.create_notification(notification_data, session)

    async def create_order_completed_notification(self, session: AsyncSession, order_id: str, customer_id: str,
                                                  order_code: str, note: Optional[str] = None):

        is_duplicate_customer = await self.check_duplicate_notification(
            session=session,
            recipient_id=customer_id,
            notification_type=NotificationType.ORDER_COMPLETED,
            order_id=order_id
        )

        if not is_duplicate_customer:
            message = f"Cảm ơn bạn đã xác nhận nhận hàng cho đơn hàng #{order_code}. Đơn hàng đã hoàn thành."
            if note:
                message += f" {note}"

            message += " Hãy đánh giá sản phẩm để chia sẻ trải nghiệm của bạn!"

            action_data = {
                "order_id": order_id,
                "completed_at": datetime.now().isoformat(),
                "note": note,
                "can_review": True
            }

            customer_notification_data = {
                "recipient_type": RecipientType.CUSTOMER,
                "recipient_id": customer_id,
                "sender_type": RecipientType.SYSTEM,
                "sender_id": None,
                "type": NotificationType.ORDER_COMPLETED,
                "title": f"Đơn hàng #{order_code} đã hoàn thành",
                "message": message,
                "order_id": order_id,
                "action_type": ActionType.REVIEW_ORDER,
                "action_data": json.dumps(action_data)
            }

            await notification_repository.create_notification(customer_notification_data, session)

        is_duplicate_admin = await self.check_duplicate_notification(
            session=session,
            recipient_id=None,
            notification_type=NotificationType.ORDER_COMPLETED_ADMIN,
            order_id=order_id
        )

        if not is_duplicate_admin:
            admin_action_data = {
                "order_id": order_id,
                "customer_id": customer_id,
                "completed_at": datetime.now().isoformat()
            }

            admin_notification_data = {
                "recipient_type": RecipientType.ADMIN,
                "recipient_id": None,
                "sender_type": RecipientType.CUSTOMER,
                "sender_id": customer_id,
                "type": NotificationType.ORDER_COMPLETED_ADMIN,
                "title": f"Đơn hàng #{order_code} đã hoàn thành",
                "message": f"Khách hàng đã xác nhận nhận hàng cho đơn hàng #{order_code}. Đơn hàng đã hoàn thành.",
                "order_id": order_id,
                "action_type": None,
                "action_data": json.dumps(admin_action_data)
            }

            await notification_repository.create_notification(admin_notification_data, session)