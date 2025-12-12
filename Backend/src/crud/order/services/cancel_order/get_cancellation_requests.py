from sqlalchemy.orm import selectinload
from src.database.models import Order
from src.crud.order.repositories import OrderRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import desc
from src.schemas.order import CancellationStatusType

order_repository = OrderRepository()


class GetCancellationRequestService:
    async def get_cancellation_requests(self, session: AsyncSession, skip: int = 0, limit: int = 20):
        condition = [
            Order.cancellation_status == CancellationStatusType.REQUESTED,
            Order.deleted_at.is_(None)
        ]
        options = [selectinload(Order.user), selectinload(Order.order_detail)]
        order_by = desc(Order.cancellation_requested_at)

        orders, total = await order_repository.get_all_order(session=session, where_conditions=condition, order_by=order_by,
                                                             skip=skip, limit=limit, options=options)

        return orders, total

    async def get_orders_by_status(self, session: AsyncSession, status: str, skip: int = 0, limit: int = 20):
        condition = [Order.status == status, Order.deleted_at.is_(None)]
        options = [selectinload(Order.user), selectinload(Order.order_detail)]
        order_by = desc(Order.created_at)

        orders, total = await order_repository.get_all_order(session=session, where_conditions=condition,
                                                             order_by=order_by, skip=skip, limit=limit, options=options)

        return orders, total


