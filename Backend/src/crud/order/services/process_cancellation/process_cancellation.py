from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from fastapi import Request
from src.crud.order.services.cancel_order.cancellation_notification import CancelNotificationService
from src.crud.order.services.cancel_order.inventory_restoration import InventoryRestorationService
from src.crud.order.services.process_cancellation.refund_processing import RefundProcessingService
from src.database.models import Order
from src.crud.order.repositories import OrderRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.order import OrderException
from src.schemas.order import ProcessCancellationRequest, CancellationStatusType, CancellationAction
import logging

logger = logging.getLogger(__name__)


order_repository = OrderRepository()

inventory_restoration_service = InventoryRestorationService()
refund_processing_service = RefundProcessingService()
cancellation_notification_service = CancelNotificationService()


class ProcessCancellationService:
    async def approve_cancellation(self, session: AsyncSession, order_id: str, admin_note: Optional[str], request: Request):
        conditions = [Order.id == order_id, Order.deleted_at.is_(None)]
        options = [
            selectinload(Order.order_detail),
            selectinload(Order.user),
            selectinload(Order.payments)
        ]
        order = await order_repository.get_order(session=session, where_conditions=conditions, options=options)

        if not order:
            raise OrderException.not_found()

        condition_update = and_(Order.id == order_id)
        await order_repository.update_order_some_field(condition_update, {
            "status": "cancelled",
            "cancellation_status": CancellationStatusType.APPROVED,
            "updated_at": datetime.now()
        }, session)

        await inventory_restoration_service.restore_all(session, order_id)

        success = await refund_processing_service.process_refund_if_paid(session, order, request)

        if success:
            await cancellation_notification_service.notify_cancellation_approved(
                session=session,
                order_id=order_id,
                customer_id=str(order.user_id),
                order_code=order.code,
                admin_note=admin_note
            )


    async def reject_cancellation(self, session: AsyncSession, order_id: str, reject_reason: str, request: Request):
        conditions = [Order.id == order_id, Order.deleted_at.is_(None)]
        options = [
            selectinload(Order.order_detail),
            selectinload(Order.user),
            selectinload(Order.payments)
        ]
        order = await order_repository.get_order(session=session, where_conditions=conditions, options=options)

        if not order:
            raise OrderException.not_found()

        current_reason = order.cancellation_reason or ""
        new_reason = f"{current_reason} | Từ chối: {reject_reason}"

        condition = and_(Order.id == order_id)
        await order_repository.update_order_some_field(condition, {
            "cancellation_status": CancellationStatusType.REJECTED,
            "cancellation_reason": new_reason,
            "updated_at": datetime.now()
        }, session)

        await cancellation_notification_service.notify_cancellation_rejected(
            session=session,
            order_id=order_id,
            customer_id=str(order.user_id),
            order_code=order.code,
            reject_reason=reject_reason
        )


    async def process_cancellation_by_admin(self, order_id: str, data: ProcessCancellationRequest, request: Request,
                                           session: AsyncSession):
        conditions = [Order.id == order_id, Order.deleted_at.is_(None)]
        options = [
            selectinload(Order.order_detail),
            selectinload(Order.user),
            selectinload(Order.payments)
        ]
        order = await order_repository.get_order(session=session, where_conditions=conditions, options=options)

        if not order:
            OrderException.not_found()

        if order.cancellation_status != CancellationStatusType.REQUESTED:
            OrderException.not_request_cancelled()

        message = ""
        try:
            if data.action == CancellationAction.APPROVE:
                await self.approve_cancellation(session, order_id, data.admin_note, request)
                message = f"Đã chấp thuận hủy đơn hàng #{order.code}"

            elif data.action == CancellationAction.REJECT:
                await self.reject_cancellation(session, order_id, data.reject_reason, request)

                message = f"Đã từ chối hủy đơn hàng #{order.code}"
            else:
                OrderException.action_invalid()

            await session.commit()

            return message, {
                "order_id": order_id,
                "order_code": order.code,
                "action": data.action,
                "cancellation_status": order.cancellation_status.value
            }

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to process cancellation")
            OrderException.error_cancelled()


