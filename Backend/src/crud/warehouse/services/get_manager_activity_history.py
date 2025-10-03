from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import and_, or_, desc
from src.crud.stock.repositories import StockRepository
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User, StockTransaction, StockTransfer
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import TransactionType
from src.schemas.warehouse import ManagerActivityFilter

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()
stock_repository = StockRepository()

class GetManagerActivityHistoryService:
    async def get_manager_activity_history(self, user_id: str, filters: ManagerActivityFilter, session: AsyncSession,
                                           skip: int = 0, limit: int = 10):
        condition_user = and_(User.id == user_id, User.deleted_at.is_(None))
        joins_user = [
            selectinload(User.warehouse),
            selectinload(User.managed_warehouses)
        ]
        user = await user_repository.get_user(condition_user, session, joins_user)
        if not user:
            AuthException.user_not_found()

        if not user.is_staff:
            UserException.only_staff_activity_can_be_viewed()

        if filters.from_date and filters.to_date:
            if filters.from_date > filters.to_date:
                WareHouseException.check_date()

        current_warehouse = None
        if user.warehouse_id and user.warehouse:
            current_warehouse = {
                "id": str(user.warehouse.id),
                "name": user.warehouse.name,
                "code": user.warehouse.code,
                "address": user.warehouse.address,
                "is_active": user.warehouse.is_active,
                "is_default": user.warehouse.is_default
            }

        condition_manage_warehouse = [Warehouse.manager_id == user_id]
        managed_warehouses = await warehouse_repository.get_all_warehouse(
            condition_manage_warehouse,
            session,
            skip=0,
            limit=1000
        )
        managed_warehouses_data = [
            {
                "id": str(wh.id),
                "name": wh.name,
                "code": wh.code,
                "address": wh.address,
                "is_active": wh.is_active,
                "is_default": wh.is_default
            }
            for wh in managed_warehouses
        ]

        summary_data = await warehouse_repository.get_activity_summary(
            user_id=user_id,
            session=session,
            warehouse_id=filters.warehouse_id,
            from_date=filters.from_date,
            to_date=filters.to_date
        )

        transactions = await self.get_stock_transactions_by_user(
            user_id=user_id,
            session=session,
            warehouse_id=filters.warehouse_id,
            transaction_type=filters.transaction_type,
            from_date=filters.from_date,
            to_date=filters.to_date,
            skip=skip,
            limit=limit
        )

        transactions_response = [
            {
                "id": str(t.id),
                "warehouse_id": str(t.warehouse_id),
                "transaction_type": t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(
                    t.transaction_type),
                "quantity": t.quantity,
                "previous_quantity": t.previous_quantity,
                "new_quantity": t.new_quantity,
                "unit_cost": t.unit_cost,
                "total_cost": t.total_cost,
                "reference_type": t.reference_type,
                "reference_id": str(t.reference_id) if t.reference_id else None,
                "reason": t.reason,
                "note": t.note,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "product_variant_id": str(t.product_variant_id)
            }
            for t in transactions
        ]

        transfers_sent = await self.get_stock_transfers_sent_by_user(
            user_id=user_id,
            session=session,
            warehouse_id=filters.warehouse_id,
            from_date=filters.from_date,
            to_date=filters.to_date,
            skip=0,
            limit=limit * 4
        )

        transfers_received = await self.get_stock_transfers_received_by_user(
            user_id=user_id,
            session=session,
            warehouse_id=filters.warehouse_id,
            from_date=filters.from_date,
            to_date=filters.to_date,
            skip=0,
            limit=limit * 4
        )

        all_transfers = list(transfers_sent) + list(transfers_received)

        seen_ids = set()
        unique_transfers = []
        for t in all_transfers:
            if t.id not in seen_ids:
                seen_ids.add(t.id)
                unique_transfers.append(t)

        unique_transfers.sort(key=lambda x: x.requested_at, reverse=True)

        unique_transfers = unique_transfers[:limit]

        transfers_response = [
            {
                "id": str(t.id),
                "transfer_code": t.transfer_code,
                "from_warehouse_id": str(t.from_warehouse_id),
                "to_warehouse_id": str(t.to_warehouse_id),
                "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
                "reason": t.reason,
                "note": t.note,
                "requested_at": t.requested_at.isoformat() if t.requested_at else None,
                "approved_at": t.approved_at.isoformat() if t.approved_at else None,
                "shipped_at": t.shipped_at.isoformat() if t.shipped_at else None,
                "received_at": t.received_at.isoformat() if t.received_at else None
            }
            for t in unique_transfers
        ]

        manager_name = f"{user.first_name} {user.last_name}".strip()

        return {
            "manager_id": str(user_id),
            "manager_name": manager_name,
            "warehouse_role": user.warehouse_role,
            "current_warehouse": current_warehouse,
            "managed_warehouses": managed_warehouses_data,
            "summary": {
                "total_transactions": summary_data.get("total_transactions", 0),
                "total_inbound": summary_data.get("total_inbound", 0),
                "total_outbound": summary_data.get("total_outbound", 0),
                "total_adjustments": summary_data.get("total_adjustments", 0),
                "total_transfers_sent": summary_data.get("total_transfers_sent", 0),
                "total_transfers_received": summary_data.get("total_transfers_received", 0),
                "total_value_handled": summary_data.get("total_value_handled", 0),
                "first_activity_date": summary_data.get("first_activity_date").isoformat() if summary_data.get(
                    "first_activity_date") else None,
                "last_activity_date": summary_data.get("last_activity_date").isoformat() if summary_data.get(
                    "last_activity_date") else None
            },
            "recent_transactions": transactions_response,
            "recent_transfers": transfers_response
        }


    async def get_stock_transactions_by_user(self, user_id: str,
                                             session: AsyncSession,
                                             warehouse_id: Optional[str] = None,
                                             transaction_type: Optional[TransactionType] = None,
                                             from_date: Optional[datetime] = None,
                                             to_date: Optional[datetime] = None,
                                             skip: int = 0, limit: int = 10):
        condition = [StockTransaction.performed_by == user_id]

        if warehouse_id:
            condition.append(StockTransaction.warehouse_id == warehouse_id)

        if transaction_type:
            condition.append(StockTransaction.transaction_type == transaction_type)

        if from_date:
            condition.append(StockTransaction.created_at >= from_date)

        if to_date:
            condition.append(StockTransaction.created_at < to_date + timedelta(days=1))

        order_by_clause = desc(StockTransaction.created_at)

        transactions, _ = await stock_repository.get_stock_transactions(condition, session, skip, limit, None, order_by_clause)

        return transactions


    async def get_stock_transfers_sent_by_user(self, user_id: str,
                                             session: AsyncSession,
                                             warehouse_id: Optional[str] = None,
                                             from_date: Optional[datetime] = None,
                                             to_date: Optional[datetime] = None,
                                             skip: int = 0, limit: int = 10):
        condition = [
            or_(
                StockTransfer.requested_by == user_id,
                StockTransfer.approved_by == user_id,
                StockTransfer.shipped_by == user_id
            )
        ]

        if warehouse_id:
            condition.append(StockTransfer.from_warehouse_id == warehouse_id)

        if from_date:
            condition.append(StockTransfer.requested_at >= from_date)

        if to_date:
            condition.append(StockTransfer.requested_at < to_date + timedelta(days=1))

        order_by_clause = desc(StockTransfer.requested_at)

        transfers, _ = await stock_repository.get_stock_transfers(condition, session, skip, limit, None, order_by_clause)

        return transfers


    async def get_stock_transfers_received_by_user(self, user_id: str,
                                                   session: AsyncSession,
                                                   warehouse_id: Optional[str] = None,
                                                   from_date: Optional[datetime] = None,
                                                   to_date: Optional[datetime] = None,
                                                   skip: int = 0, limit: int = 10):
        condition = [StockTransfer.received_by == user_id]

        if warehouse_id:
            condition.append(StockTransfer.to_warehouse_id == warehouse_id)

        if from_date:
            condition.append(StockTransfer.received_at >= from_date)

        if to_date:
            condition.append(StockTransfer.received_at < to_date + timedelta(days=1))

        order_by_clause = desc(StockTransfer.received_at)

        transfers, _ = await stock_repository.get_stock_transfers(condition, session, skip, limit, None, order_by_clause)

        return transfers




