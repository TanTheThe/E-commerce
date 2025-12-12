from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from src.crud.order.repositories import OrderRepository
from src.crud.user.repositories import UserRepository
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.cash.repositories import CashRepository
from src.database.models import Order, User
from src.errors.order import OrderException
from src.schemas.order import PaymentStatusOrderType
from src.schemas.webhook import ShippingWebhookRequest
from src.celery_tasks.auto_received_order import auto_confirm_order_received_task

order_repository = OrderRepository()
user_repository = UserRepository()
cash_repository = CashRepository()


class WebhookShippingService:
    def __init__(self):
        self.valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['shipping', 'cancelled'],
            'shipping': ['delivered', 'cancelled'],
            'delivered': ['received'],
            'cancelled': [],
            'received': []
        }

    async def update_shipping_status(self, webhook_data: ShippingWebhookRequest, session: AsyncSession):
        try:
            condition = and_(Order.code == webhook_data.order_code)
            joins = [selectinload(Order.user)]
            order = await order_repository.get_order(condition, session, joins)

            if not order:
                OrderException.not_found()

            old_status = order.status
            new_status = webhook_data.status

            if old_status == new_status:
                OrderException.already_in_this_status()

            if new_status not in self.valid_transitions.get(old_status, []):
                OrderException.cant_change_status(old_status, new_status)

            update_data = {
                'status': new_status,
                'updated_at': datetime.now(),
            }

            if new_status == 'delivered':
                update_data['delivered_at'] = datetime.now()

            if order.payment_method == "direct":
                update_data['payment_status'] = PaymentStatusOrderType.SUCCESS

            await order_repository.update_order_some_field(condition, update_data, session)

            history_data = {
                'order_id': order.id,
                'status': new_status,
                'created_at': datetime.now()
            }

            await order_repository.create_order_status_history(history_data, session)

            cash_transaction = None
            if new_status == 'delivered' and order.payment_method == 'direct':
                cash_transaction = await self.create_cod_revenue_transaction(order, session)

            await session.commit()

            if new_status == 'delivered':
                auto_confirm_order_received_task.apply_async(
                    args=[str(order.id)],
                    countdown=259200    # 3 days = 3 * 24 * 60 * 60
                )

            response = {
                'old_status': old_status,
                'new_status': new_status,
            }

            if cash_transaction:
                response['cash_transaction'] = {
                    'id': str(cash_transaction.id),
                    'transaction_code': cash_transaction.transaction_code,
                    'amount': cash_transaction.amount,
                    'transaction_date': cash_transaction.transaction_date.isoformat()
                }

            return response

        except HTTPException:
            await session.rollback()
            raise

    async def create_cod_revenue_transaction(self, order, session: AsyncSession):
        user = order.user
        if not user:
            condition = and_(User.deleted_at.is_(None), User.id == order.user_id, User.customer_status == "active")
            user = await user_repository.get_user(condition, session)

        reference_name = f"{user.first_name} {user.last_name}" if user else None

        transaction_code = f"CT{int(datetime.now().timestamp() * 1000)}"

        transaction_data = {
            'transaction_code': transaction_code,
            'transaction_type': 'inflow',
            'category': 'revenue',
            'amount': order.total_price,
            'transaction_date': datetime.now(),
            'reference_type': 'customer',
            'reference_id': order.user_id,
            'reference_name': reference_name,
            'payment_method': 'cash',
            'notes': f"Doanh thu COD từ đơn hàng {order.code}",
            'performed_by': None
        }

        cash_transaction = await cash_repository.create_cash_transaction(transaction_data, session)

        return cash_transaction




