from datetime import datetime
from typing import List, Optional, Dict, Any

from src.crud.notification.repositories import NotificationRepository
from src.database.models import Notification
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, or_
import json

from src.errors.notification import NotificationException
from src.schemas.notification import RecipientType, NotificationType, ActionType

notification_repository = NotificationRepository()

class NotificationService:
    def _build_notification_response(self, notification: Notification) -> Dict[str, Any]:
        return {
            "id": str(notification.id),
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "order_id": str(notification.order_id) if notification.order_id else None,
            "action_type": notification.action_type,
            "action_data": json.loads(notification.action_data) if notification.action_data else None,
            "is_read": notification.is_read,
            "is_processed": notification.is_processed,
            "created_at": str(notification.created_at),
            "read_at": str(notification.read_at),
            "processed_at": str(notification.processed_at),
        }

    async def get_notifications_admin_service(self, session: AsyncSession, unread_only: bool = False,
                                              action_required: bool = False, skip: int = 0, limit: int = 30):
        conditions = [Notification.recipient_type == RecipientType.ADMIN]

        if unread_only:
            conditions.append(Notification.is_read == False)

        if action_required:
            conditions.extend(
                [Notification.action_type.isnot(None), Notification.is_processed == False]
            )

        notifications, total = await notification_repository.get_all_notifications(
            conditions, session, None, skip, limit
        )

        response = [self._build_notification_response(notif) for notif in notifications]

        return {
            "data": response,
            "total": total,
        }

    async def get_notifications_customer_service(self, session: AsyncSession, user_id: str, unread_only: bool = False, skip: int = 0, limit: int = 30):
        conditions = [
            Notification.recipient_type == RecipientType.CUSTOMER,
            Notification.recipient_id == user_id
        ]

        if unread_only:
            conditions.append(Notification.is_read == False)

        notifications, total = await notification_repository.get_all_notifications(
            conditions, session, None, skip, limit
        )

        response = [self._build_notification_response(notif) for notif in notifications]

        return {
            "data": response,
            "total": total,
        }

    async def get_unread_count_service(self, session: AsyncSession, recipient_type: str, user_id: str = None):
        conditions = [
            Notification.recipient_type == recipient_type,
            Notification.is_read == False
        ]

        if recipient_type == RecipientType.CUSTOMER and user_id:
            conditions.append(Notification.recipient_id == user_id)

        notifications, total = await notification_repository.get_all_notifications(conditions, session, None, 0, 1000)

        return total

    # Đếm số notification cần admin action
    async def get_pending_actions_count(self, session: AsyncSession, action_type: Optional[str] = None):
        conditions = [
            Notification.recipient_type == RecipientType.ADMIN,
            Notification.action_type.isnot(None),
            Notification.is_processed == False
        ]

        if action_type:
            conditions.append(Notification.action_type == action_type)

        notifications, total = await notification_repository.get_all_notifications(
            conditions, session, None, 0, 1000
        )

        return total

    # Gửi thông báo hủy đơn hàng khi đơn hàng ở trạng thái 'pending'
    async def create_order_cancelled_notification(self, session: AsyncSession, order_id: str, customer_id: str, order_code: str,
                                                  reason: str = "Khách hàng tự động hủy đơn hàng"):
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
                                                        admin_note: Optional[str] = None):
        message = f"Yêu cầu hủy đơn hàng #{order_code} đã được chấp thuận."
        if admin_note:
            message += f" Ghi chú: {admin_note}"

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": None,
            "type": NotificationType.ORDER_CANCELLATION_APPROVED,
            "title": f"Đơn hàng #{order_code} đã được hủy",
            "message": message,
            "order_id": order_id,
            "action_type": None,
            "action_data": None
        }

        return await notification_repository.create_notification(notification_data, session)

    # Gửi thông báo khi admin reject yêu cầu hủy đơn
    async def create_cancellation_rejected_notification(self, session: AsyncSession, order_id: str, customer_id: str, order_code: str,
                                                        reject_reason: str):
        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": None,
            "type": NotificationType.ORDER_CANCELLATION_REJECTED,
            "title": f"Yêu cầu hủy đơn hàng #{order_code} bị từ chối",
            "message": f"Yêu cầu hủy đơn hàng #{order_code} không được chấp thuận. Lý do: {reject_reason}",
            "order_id": order_id,
            "action_type": None,
            "action_data": None
        }

        return await notification_repository.create_notification(notification_data, session)
    
    async def create_assign_special_offer_notification(self, session: AsyncSession, special_offer_id: str, special_offer_name: str, 
                                                       customer_id: str, admin_note: Optional[str] = None):
        message = f"Bạn vừa nhận được khuyến mãi #{special_offer_name} từ cửa hàng."
        if admin_note:
            message += f" Ghi chú: {admin_note}"

        notification_data = {
            "recipient_type": RecipientType.CUSTOMER,
            "recipient_id": customer_id,
            "sender_type": RecipientType.ADMIN,
            "sender_id": None,
            "type": NotificationType.SPECIAL_OFFER_ASSIGNED,
            "title": f"Vừa nhận được khuyến mãi #{special_offer_name}",
            "message": message,
            "special_offer_id": special_offer_id,
            "action_type": None,
            "action_data": None
        }

        return await notification_repository.create_notification(notification_data, session)

    # Đánh dấu notification đã được xử lý
    async def mark_as_processed(self, session: AsyncSession, notification_id: str):
        condition = [Notification.id == notification_id]
        notification = await notification_repository.get_notification(condition, session)
        if not notification:
            NotificationException.notification_not_found()

        notification.is_processed = True
        notification.processed_at = datetime.now()
        session.add(notification)
        await session.commit()

        return True

    async def mark_as_read(self, session: AsyncSession, notification_ids: List[str], user_id: Optional[str] = None):
        conditions = [Notification.id.in_(notification_ids)]
        if user_id:
            conditions.append(
                or_(
                    Notification.recipient_type == "admin",
                    and_(
                        Notification.recipient_type == "customer",
                        Notification.recipient_id == user_id
                    )
                )
            )

        notifications, _ = await notification_repository.get_all_notifications(conditions, session, None, 0, 1000)

        marked_count = 0
        for notification in notifications:
            if not notification.is_read:
                notification.is_read = True
                notification.read_at = datetime.now()
                session.add(notification)
                marked_count += 1

        await session.commit()
        return len(notifications)

