import uuid
from src.database.models import CashTransaction
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime


class CashRepository:
    async def create_cash_transaction(self, transaction_data: dict, session: AsyncSession):
        new_transaction = CashTransaction(
            id=uuid.uuid4(),
            transaction_code=transaction_data['transaction_code'],
            transaction_type=transaction_data['transaction_type'],
            category=transaction_data['category'],
            amount=transaction_data['amount'],
            transaction_date=transaction_data.get('transaction_date', datetime.now()),
            reference_type=transaction_data.get('reference_type'),
            reference_id=transaction_data.get('reference_id'),
            reference_name=transaction_data.get('reference_name'),
            payment_method=transaction_data['payment_method'],
            notes=transaction_data.get('notes'),
            performed_by=transaction_data.get('performed_by'),
            created_at=datetime.now()
        )

        session.add(new_transaction)
        await session.flush()
        return new_transaction

