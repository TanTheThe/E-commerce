from datetime import datetime
from sqlalchemy.orm import selectinload
from src.crud.order.services.cancel_order.notification_cancel_service import NotificationCancelService
from src.database.models import Order, OrderStatusHistory
from src.crud.order.repositories import OrderRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.authentication import AuthException
from src.errors.order import OrderException
from src.schemas.order import CancellationStatusType, OrderStatus

order_repository = OrderRepository()

notification_cancel_service = NotificationCancelService()


class ConfirmOrderReceivedService:
    async def confirm_order_received_service(self, order_id: str, user_id: str, session: AsyncSession):
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
            OrderException.cant_update_cancel_order()
        if order.cancellation_status == CancellationStatusType.APPROVED:
            OrderException.cant_reverse_cancel_order()

        if str(order.user_id) != user_id:
            raise AuthException.unauthorized()

        if order.status != OrderStatus.DELIVERED.value:
            raise OrderException.current_status_cant_pick_up(order.status)

        if order.status == OrderStatus.RECEIVED.value:
            raise OrderException.already_received()

        old_status = order.status

        update_data = {
            "status": OrderStatus.RECEIVED.value,
            "received_at": datetime.now(),
            "updated_at": datetime.now()
        }

        order_updated = await order_repository.update_order(order, update_data, session)

        history_entry = OrderStatusHistory(
            order_id=order_id,
            status=OrderStatus.RECEIVED.value,
            created_at=datetime.now(),
        )
        session.add(history_entry)

        await notification_cancel_service.notify_status_change(
            session=session,
            order=order_updated,
            old_status=old_status,
            new_status=OrderStatus.RECEIVED.value,
            note="Khách hàng xác nhận đã nhận hàng"
        )

        await session.commit()

        return order_updated

