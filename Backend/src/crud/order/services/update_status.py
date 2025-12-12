from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from src.crud.notification.services.create_notification import CreateNotificationService
from src.crud.order.services.cancel_order.notification_cancel_service import NotificationCancelService
from src.database.models import Order, OrderStatusHistory
from src.crud.order.repositories import OrderRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.order import OrderException
from src.schemas.order import CancellationStatusType, StatusUpdateModel, OrderStatus, STATUS_TRANSITION_RULES

order_repository = OrderRepository()

create_notification_service = CreateNotificationService()
notification_cancel_service = NotificationCancelService()


class UpdateStatusOrderService:
    async def update_status(self, order_id: str, request: StatusUpdateModel, session: AsyncSession):
        conditions_order = [
            Order.id == order_id,
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

        old_status = order.status

        if order.cancellation_status == CancellationStatusType.REQUESTED:
            OrderException.cant_update_cancel_order()

        if order.cancellation_status == CancellationStatusType.APPROVED:
            OrderException.cant_reverse_cancel_order()

        self.validate_status_transition(old_status, request.status)

        update_data = {
            "status": request.status,
            "updated_at": datetime.now()
        }

        if request.status == OrderStatus.DELIVERED:
            update_data["delivered_at"] = datetime.now()

        if request.note:
            existing_note = order.note or ""
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            new_note_entry = f"[{timestamp}] {request.status.value}: {request.note}"

            if existing_note:
                update_data["note"] = f"{existing_note}\n{new_note_entry}"
            else:
                update_data["note"] = new_note_entry

        order_updated = await order_repository.update_order(order, update_data, session)

        history_entry = OrderStatusHistory(
            order_id=order_id,
            status=order_updated.status,
            created_at=datetime.now()
        )
        session.add(history_entry)

        await notification_cancel_service.notify_status_change(
            session=session,
            order=order_updated,
            old_status=old_status,
            new_status=request.status,
            note=request.note
        )

        await session.commit()

        return order_updated, old_status


    def validate_status_transition(self, current_status: str, new_status: str):
        if current_status not in [s.value for s in OrderStatus]:
            raise OrderException.invalid_current_status()

        if current_status == new_status:
            OrderException.status_already_set()

        current_status_enum = OrderStatus(current_status)
        allowed_next = STATUS_TRANSITION_RULES[current_status_enum]["allowed_next"]

        if OrderStatus(new_status) not in allowed_next:
            raise OrderException.invalid_status_transition(
                current_status,
                new_status,
            )