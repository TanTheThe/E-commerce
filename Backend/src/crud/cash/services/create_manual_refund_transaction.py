from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.user.repositories import UserRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.cash.repositories import CashRepository
from src.database.models import User, ReturnOrder, CashTransaction
from src.errors.authentication import AuthException
from src.errors.return_order import ReturnOrderException
from src.schemas.cash import PaymentMethod, RefundStatus
import logging

logger = logging.getLogger(__name__)

return_order_repository = ReturnOrderRepository()
user_repository = UserRepository()
cash_repository = CashRepository()


class ManualRefundCashService:
    async def check_idempotency(self, idempotency_key: str, session: AsyncSession) -> Optional[dict]:
        if not idempotency_key:
            return None

        conditions = [
            CashTransaction.idempotency_key == idempotency_key,
            CashTransaction.deleted_at.is_(None)
        ]

        existing_transaction = await cash_repository.get_cash_transaction(session=session, where_conditions=conditions)

        if existing_transaction:
            return {
                "transaction_id": str(existing_transaction.id),
                "transaction_code": existing_transaction.transaction_code,
                "amount": existing_transaction.amount,
                "payment_method": existing_transaction.payment_method,
                "transaction_date": existing_transaction.transaction_date.isoformat(),
                "reference_name": existing_transaction.reference_name,
                "notes": existing_transaction.notes
            }

        return None


    async def get_total_refunded(self, return_order_id: str, session: AsyncSession) -> int:
        conditions = [
            CashTransaction.category == 'refund',
            CashTransaction.related_return_order_id == return_order_id,
            CashTransaction.status == 'completed',
            CashTransaction.deleted_at.is_(None)
        ]

        select_columns = [
            func.coalesce(func.sum(CashTransaction.amount), 0).label("total_refunded")
        ]

        cash = await cash_repository.get_cash_transaction(session=session, where_conditions=conditions,
                                                          select_columns=select_columns)

        return cash.total_refunded if cash else 0

    async def calculate_refund_status(self, total_refund: int, already_refunded: int, new_amount: int):
        total_after_refund = already_refunded + new_amount

        if total_after_refund >= total_refund:
            return RefundStatus.COMPLETED
        elif total_after_refund > 0:
            return RefundStatus.PARTIAL
        else:
            return RefundStatus.PENDING


    async def create_manual_refund_transaction(self, return_order_id: str, amount: int, payment_method: PaymentMethod,
                                               notes: Optional[str], transaction_date: Optional[datetime],
                                               idempotency_key: Optional[str], performed_by_id: Optional[str],
                                               session: AsyncSession):
        try:
            if idempotency_key:
                existing = await self.check_idempotency(idempotency_key, session)
                if existing:
                    logger.info(f"Duplicate refund request detected: {idempotency_key}")
                    return existing

            conditions = [ReturnOrder.id == return_order_id, ReturnOrder.deleted_at.is_(None)]
            options = [
                selectinload(ReturnOrder.order),
                selectinload(ReturnOrder.return_items)
            ]

            return_order = await return_order_repository.get_return_order(session=session, where_conditions=conditions,
                                                                          options=options)
            if not return_order:
                ReturnOrderException.return_doesnt_exist()

            if return_order.status != "completed":
                ReturnOrderException.must_be_in_completed()

            total_refund = return_order.total_refund_amount

            if total_refund == 0:
                total_refund = sum(item.refund_amount for item in return_order.return_items)
                return_order.total_refund_amount = total_refund

            if total_refund <= 0:
                ReturnOrderException.return_order_doesnt_specify_refund_amount()

            already_refunded = return_order.refunded_amount

            db_refunded = await self.get_total_refunded(str(return_order_id), session)
            if already_refunded != db_refunded:
                logger.warning(
                    f"Refunded amount mismatch for return_order {return_order_id}: "
                    f"DB field={already_refunded}, Calculated={db_refunded}"
                )
                already_refunded = db_refunded
                return_order.refunded_amount = db_refunded

            remaining_amount = total_refund - already_refunded

            if remaining_amount <= 0:
                ReturnOrderException.return_order_has_been_refunded()

            if amount > remaining_amount:
                ReturnOrderException.refund_amount_exceeds_remaining_balance()

            user_id = return_order.user_id
            conditions = [User.id == user_id, User.deleted_at.is_(None)]
            user = await user_repository.get_user(session=session, where_conditions=conditions)

            if not user:
                AuthException.user_not_found()

            reference_name = f"{user.first_name} {user.last_name}".strip()

            transaction_code = f"RF{int(datetime.now().timestamp() * 1000)}"

            default_notes = (
                f"Hoàn tiền thủ công cho đơn hàng {return_order.order.code} "
                f"- Return order #{return_order_id}"
            )
            final_notes = f"{default_notes}\n{notes}" if notes else default_notes

            new_refund_status = await self.calculate_refund_status(
                total_refund,
                already_refunded,
                amount
            )

            transaction_data = {
                'transaction_code': transaction_code,
                'transaction_type': 'outflow',
                'category': 'refund',
                'amount': amount,
                'transaction_date': transaction_date or datetime.now(),
                'reference_type': 'customer',
                'reference_id': user_id,
                'reference_name': reference_name,
                'payment_method': payment_method.value,
                'notes': final_notes,
                'performed_by': performed_by_id,
                'idempotency_key': idempotency_key,
                'related_return_order_id': return_order_id,
                'related_order_id': return_order.order_id,
                'status': 'completed'
            }

            cash_transaction = await cash_repository.create_cash_transaction(
                transaction_data,
                session
            )

            return_order.refund_status = new_refund_status.value
            return_order.refunded_amount = already_refunded + amount
            return_order.updated_at = datetime.now()

            if new_refund_status == RefundStatus.COMPLETED:
                return_order.fully_refunded_at = datetime.now()

            await session.commit()

            return {
                "transaction_id": str(cash_transaction.id),
                "transaction_code": cash_transaction.transaction_code,
                "amount": cash_transaction.amount,
                "payment_method": cash_transaction.payment_method,
                "transaction_date": cash_transaction.transaction_date.isoformat(),
                "reference_name": cash_transaction.reference_name,
                "notes": cash_transaction.notes,
                "refund_summary": {
                    "total_refund": total_refund,
                    "already_refunded": already_refunded,
                    "current_refund": amount,
                    "remaining": total_refund - (already_refunded + amount),
                    "status": new_refund_status.value
                }
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating manual refund: {e}")
            raise



