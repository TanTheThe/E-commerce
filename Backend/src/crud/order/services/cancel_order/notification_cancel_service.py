from typing import Optional
from src.crud.notification.services.create_notification import CreateNotificationService
from src.database.models import Order
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.order import OrderStatus

create_notification_service = CreateNotificationService()


class NotificationCancelService:
    async def notify_status_change(self, session: AsyncSession, order: Order, old_status: str, new_status: str,
                                   note: Optional[str] = None) -> None:
        notification_map = {
            OrderStatus.CONFIRMED.value: self.notify_order_confirmed,
            OrderStatus.SHIPPING.value: self.notify_order_shipping,
            OrderStatus.DELIVERED.value: self.notify_order_delivered,
            OrderStatus.RECEIVED.value: self.notify_order_received,
        }

        notify_func = notification_map.get(new_status)
        if notify_func:
            await notify_func(session, order, note)


    async def notify_order_confirmed(self, session: AsyncSession, order: Order, note: Optional[str]):
        await create_notification_service.create_order_confirmed_notification(
            session=session,
            order_id=str(order.id),
            customer_id=str(order.user_id),
            order_code=order.code,
            note=note
        )


    async def notify_order_shipping(self, session: AsyncSession, order: Order, note: Optional[str]):
        await create_notification_service.create_order_shipping_notification(
            session=session,
            order_id=str(order.id),
            customer_id=str(order.user_id),
            order_code=order.code,
            note=note
        )


    async def notify_order_delivered(self, session: AsyncSession, order: Order, note: Optional[str]):
        await create_notification_service.create_order_delivered_notification(
            session=session,
            order_id=str(order.id),
            customer_id=str(order.user_id),
            order_code=order.code,
            note=note
        )


    async def notify_order_received(self, session: AsyncSession, order: Order, note: Optional[str]):
        await create_notification_service.create_order_completed_notification(
            session=session,
            order_id=str(order.id),
            customer_id=str(order.user_id),
            order_code=order.code,
            note=note
        )