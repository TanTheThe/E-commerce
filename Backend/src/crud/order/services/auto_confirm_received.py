from datetime import datetime
from sqlalchemy.orm import selectinload
from src.database.models import Order_Detail, Order
from src.crud.order.repositories import OrderRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.schemas.order import CancellationStatusType

order_repository = OrderRepository()

class AutoConfirmReceivedService:
    async def auto_confirm_received(self, order_id: str, session: AsyncSession):
        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        options = [selectinload(Order.order_detail).load_only(Order_Detail.product_id)]

        order = await order_repository.get_order(condition, session, options)

        if not order:
            print(f"Order {order_id} not found")
            return None

        if order.status != "delivered":
            print(f"Order {order_id} is no longer in 'delivered' status. Current: {order.status}")
            return None

        if order.cancellation_status in [CancellationStatusType.REQUESTED, CancellationStatusType.APPROVED]:
            print(f"Order {order_id} has cancellation status: {order.cancellation_status}")
            return None

        update_data = {
            "status": "received",
            "received_at": datetime.now(),
        }

        await order_repository.update_order_some_field(condition, update_data, session)

        history_dict = {
            "order_id": order_id,
            "status": "received",
            "created_at": datetime.now(),
        }

        history_entry = await order_repository.create_order_status_history(history_dict, session)

        await session.commit()

        print(f"Order {order_id} auto-confirmed as received")

        return {
            "order_id": order_id,
            "status": "received",
            "received_at": datetime.now(),
        }






