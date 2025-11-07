from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from src.crud.order.repositories import OrderRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.user.repositories import UserRepository
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.cash.repositories import CashRepository
from src.database.models import Order, User, ReturnOrder
from src.errors.order import OrderException
from src.errors.return_order import ReturnOrderException
from src.schemas.order import PaymentStatusOrderType
from src.schemas.webhook import ShippingWebhookRequest
from src.celery_tasks.auto_received_order import auto_confirm_order_received_task

return_order_repository = ReturnOrderRepository()
user_repository = UserRepository()
cash_repository = CashRepository()


class ManualRefundCashService:
    async def create_manual_refund_transaction(self, return_order_id: str, amount: int, payment_method: str,
                                               notes: Optional[str], transaction_date: Optional[datetime],
                                               session: AsyncSession):

        conditions = [ReturnOrder.id == return_order_id]
        joins = [
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.user),
            selectinload(ReturnOrder.return_items)
        ]

        return_order = await return_order_repository.get_return_order(conditions, session, joins)
        if not return_order:
            ReturnOrderException.return_doesnt_exist()

        if return_order.status != "completed":
            ReturnOrderException.must_be_in_completed()

        total_refund = sum(item.refund_amount for item in return_order.return_items)
        if amount > total_refund:
            ReturnOrderException.amount_greater_than_total_refund()

        user = return_order.user
        if not user:
            condition = and_(
                User.deleted_at.is_(None),
                User.id == return_order.user_id
            )
            user = await user_repository.get_user(condition, session)

        reference_name = f"{user.first_name} {user.last_name}" if user else None

        transaction_code = f"CT{int(datetime.now().timestamp() * 1000)}"

        default_notes = f"Hoàn tiền thủ công cho đơn hàng {return_order.order.code} - Return order #{return_order.id}"
        final_notes = f"{default_notes}\n{notes}" if notes else default_notes

        transaction_data = {
            'transaction_code': transaction_code,
            'transaction_type': 'outflow',
            'category': 'refund',
            'amount': amount,
            'transaction_date': transaction_date or datetime.now(),
            'reference_type': 'customer',
            'reference_id': return_order.user_id,
            'reference_name': reference_name,
            'payment_method': payment_method,
            'notes': final_notes,
            'performed_by': None
        }

        cash_transaction = await cash_repository.create_cash_transaction(
            transaction_data,
            session
        )

        await session.commit()

        return {
            "transaction_id": str(cash_transaction.id),
            "transaction_code": cash_transaction.transaction_code,
            "amount": cash_transaction.amount,
            "payment_method": cash_transaction.payment_method,
            "transaction_date": cash_transaction.transaction_date.isoformat(),
            "reference_name": cash_transaction.reference_name,
            "notes": cash_transaction.notes
        }





