from typing import Optional
from src.crud.notification.services.create_notification import CreateNotificationService
from sqlmodel.ext.asyncio.session import AsyncSession

create_notification_service = CreateNotificationService()


class CancelNotificationService:
    async def notify_cancellation_approved(self, session: AsyncSession, order_id: str,
                                           customer_id: str, order_code: str, admin_note: Optional[str] = None):
        await create_notification_service.create_cancellation_approved_notification(
            session=session,
            order_id=order_id,
            customer_id=customer_id,
            order_code=order_code,
            admin_note=admin_note
        )


    async def notify_cancellation_rejected(self, session: AsyncSession, order_id: str,
                                           customer_id: str, order_code: str, reject_reason: str):
        await create_notification_service.create_cancellation_rejected_notification(
            session=session,
            order_id=order_id,
            customer_id=customer_id,
            order_code=order_code,
            reject_reason=reject_reason
        )


    async def notify_order_cancelled(self, session: AsyncSession, order_id: str,
                                     customer_id: str, order_code: str, reason: str):
        await create_notification_service.create_order_cancelled_notification(
            session=session,
            order_id=order_id,
            customer_id=customer_id,
            order_code=order_code,
            reason=reason
        )


    async def notify_cancellation_requested(self, session: AsyncSession, order_id: str, customer_id: str,
                                            order_code: str, reason: str, reason_detail: Optional[str] = None):
        await create_notification_service.create_cancellation_request_notification(
            session=session,
            order_id=order_id,
            customer_id=customer_id,
            order_code=order_code,
            reason=reason,
            reason_detail=reason_detail
        )

