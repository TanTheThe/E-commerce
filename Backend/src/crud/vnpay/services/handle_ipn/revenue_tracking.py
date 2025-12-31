from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.cash.repositories import CashRepository
from src.database.models import Order, Payment, CashTransaction


cash_repository = CashRepository()

class RevenueTrackingService:
    async def create_revenue_transaction(self, order: Order, payment: Payment, transaction_date: datetime,
                                         session: AsyncSession) -> CashTransaction:
        user = order.user
        reference_name = f"{user.first_name} {user.last_name}" if user else None

        transaction_code = f"CT{int(datetime.now().timestamp() * 1000)}"

        transaction_data = {
            'transaction_code': transaction_code,
            'transaction_type': 'inflow',
            'category': 'revenue',
            'amount': order.total_price,
            'transaction_date': transaction_date or datetime.now(),
            'reference_type': 'customer',
            'reference_id': order.user_id,
            'reference_name': reference_name,
            'payment_method': 'e_wallet',
            'notes': f"Doanh thu VNPay từ đơn hàng {order.code} - Giao dịch {payment.transaction_no}",
            'performed_by': None
        }

        return await cash_repository.create_cash_transaction(transaction_data, session)