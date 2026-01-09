from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from src.cache import cache_service, CacheKeys
from src.crud.order.repositories import OrderRepository
from src.crud.user.repositories import UserRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.cash.repositories import CashRepository
from src.database.models import Order, User
from src.errors.order import OrderException
from src.errors.warehouse import WareHouseException
from src.schemas.order import PaymentStatusOrderType, OrderStatus
from src.schemas.webhook import ShippingWebhookRequest
from src.celery_tasks.auto_received_order import auto_confirm_order_received_task
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

order_repository = OrderRepository()
user_repository = UserRepository()
cash_repository = CashRepository()


class WebhookShippingService:
    def __init__(self):
        self.valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.SHIPPING, OrderStatus.CANCELLED],
            OrderStatus.SHIPPING: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [OrderStatus.RECEIVED],
            OrderStatus.CANCELLED: [],
            OrderStatus.RECEIVED: []
        }
        self.IDEMPOTENCY_TTL = 86400


    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)


    async def check_idempotency(self, webhook_id: str) -> bool:
        if not webhook_id:
            return False

        cache_key = f"webhook:processed:{webhook_id}"
        return await cache_service.check_exists_with_ttl(cache_key, self.IDEMPOTENCY_TTL)


    async def acquire_order_lock(self, order_code: str, timeout: int = 10) -> bool:
        lock_key = f"order:lock:{order_code}"
        return await cache_service.acquire_lock(lock_key, timeout)


    async def release_order_lock(self, order_code: str):
        lock_key = f"order:lock:{order_code}"
        await cache_service.release_lock(lock_key)


    async def update_shipping_status(self, webhook_data: ShippingWebhookRequest, session: AsyncSession):
        if await self.check_idempotency(webhook_data.webhook_id):
            WareHouseException.webhook_processed_previously()

        if not await self.acquire_order_lock(webhook_data.order_code):
            WareHouseException.order_processed_by_different_webhook()

        try:
            conditions = [Order.code == webhook_data.order_code, Order.deleted_at.is_(None)]
            options = [selectinload(Order.user)]
            order = await order_repository.get_order(
                session=session,
                where_conditions=conditions,
                options=options,
                for_update=True
            )

            if not order:
                OrderException.not_found()

            old_status = OrderStatus(order.status)
            new_status = webhook_data.status

            if old_status == new_status:
                OrderException.already_in_this_status()

            if new_status not in self.valid_transitions.get(old_status, []):
                OrderException.cant_change_status(old_status, new_status)

            update_data = {
                'status': new_status.value,
                'updated_at': datetime.now(),
            }

            if new_status == OrderStatus.DELIVERED:
                update_data['delivered_at'] = datetime.now()

            if order.payment_method == "direct":
                update_data['payment_status'] = PaymentStatusOrderType.SUCCESS

            await order_repository.update_order_some_field(and_(*conditions), update_data, session)

            history_data = {
                'order_id': order.id,
                'status': new_status.value,
                'note': webhook_data.note,
                'created_at': datetime.now()
            }

            await order_repository.create_order_status_history(history_data, session)

            cash_transaction = None
            if new_status == OrderStatus.DELIVERED and order.payment_method == 'direct':
                cash_transaction = await self.create_cod_revenue_transaction(order, session)

            await session.commit()

            if hasattr(CacheKeys, 'order_detail'):
                await cache_service.delete(CacheKeys.order_detail(order.code))
                await cache_service.delete(CacheKeys.order_detail(str(order.id)))

            if new_status == OrderStatus.DELIVERED:
                try:
                    auto_confirm_order_received_task.apply_async(
                        args=[str(order.id)],
                        countdown=259200
                    )
                except Exception as e:
                    logger.error(f"Failed to schedule task for order {order.id}: {e}")

            response = {
                'old_status': old_status.value,
                'new_status': new_status.value,
                'order_code': order.code,
                'updated_at': update_data['updated_at'].isoformat()
            }

            if cash_transaction:
                response['cash_transaction'] = {
                    'id': str(cash_transaction.id),
                    'transaction_code': cash_transaction.transaction_code,
                    'amount': float(cash_transaction.amount),
                    'transaction_date': cash_transaction.transaction_date.isoformat()
                }

            return response

        except HTTPException as e:
            await session.rollback()
            logger.error(f"Unexpected error in webhook processing: {e}")
            raise
        finally:
            await self.release_order_lock(webhook_data.order_code)


    async def create_cod_revenue_transaction(self, order, session: AsyncSession):
        user = order.user
        if not user:
            conditions = [
                User.deleted_at.is_(None),
                User.id == order.user_id,
                User.customer_status == "active"
            ]
            user = await user_repository.get_user(session=session, where_conditions=conditions)

        reference_name = f"{user.first_name} {user.last_name}" if user else "Khách hàng"

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

        cash_transaction = await cash_repository.create_cash_transaction(
            transaction_data,
            session
        )

        return cash_transaction




