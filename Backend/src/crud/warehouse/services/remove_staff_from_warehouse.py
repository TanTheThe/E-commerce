from datetime import datetime
from typing import List
from sqlmodel import and_
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import WarehouseRole
import logging

logger = logging.getLogger(__name__)


warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class RemoveStaffService:
    async def remove_staff_from_warehouse(self, warehouse_id: str, user_id: str, session: AsyncSession):
        try:
            condition_warehouse = [Warehouse.id == warehouse_id]
            warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition_warehouse)

            if not warehouse:
                WareHouseException.warehouse_not_found()

            condition_user = [User.id == user_id, User.deleted_at.is_(None)]
            user = await user_repository.get_user(session=session, where_conditions=condition_user)
            if not user:
                AuthException.user_not_found()

            if str(user.warehouse_id) != warehouse_id:
                UserException.staff_not_in_this_warehouse()

            if user.warehouse_role == WarehouseRole.MANAGER.value:
                UserException.cant_remove_manager_in_this_function()

            await user_repository.update_user(
                condition_user,
                {"warehouse_id": None,
                 "warehouse_role": None,
                 "updated_at": datetime.now()},
                session
            )

            await session.commit()

            user_name = None
            first_name = user.first_name
            last_name = user.last_name
            if not first_name and not last_name:
                user_name = None
            user_name = f"{first_name or ''} {last_name or ''}".strip()

            return {
                "user_id": str(user.id),
                "user_name": user_name,
                "warehouse_id": str(warehouse_id),
                "warehouse_name": warehouse.name,
                "removed_at": datetime.now().isoformat()
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in remove staff from warehouse: {str(e)}")
            raise e

    async def remove_multiple_staff_from_warehouse(self, warehouse_id: str, user_ids: List[str], session: AsyncSession):
        try:
            condition_warehouse = [Warehouse.id == warehouse_id]
            warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition_warehouse)

            if not warehouse:
                WareHouseException.warehouse_not_found()

            condition_users = [
                User.id.in_(user_ids),
                User.deleted_at.is_(None),
                User.is_staff == True
            ]
            users, _ = await user_repository.get_all_users(session=session, where_conditions=condition_users, skip=0,
                                                           limit=len(user_ids) + 10)

            if len(users) != len(user_ids):
                UserException.one_staff_doesnt_exist()

            for user in users:
                if str(user.warehouse_id) != warehouse_id:
                    UserException.staff_not_in_this_warehouse()

                if user.warehouse_role == WarehouseRole.MANAGER.value:
                    UserException.cant_remove_manager_in_this_function()

            condition_remove = [
                User.id.in_(user_ids),
                User.deleted_at.is_(None)
            ]
            await user_repository.update_user(
                condition_remove,
                {
                    "warehouse_id": None,
                    "warehouse_role": None,
                    "updated_at": datetime.now()
                },
                session
            )

            await session.commit()

            removed_users = []
            user_name = None
            for user in users:
                first_name = user.first_name
                last_name = user.last_name
                if not first_name and not last_name:
                    user_name = None
                user_name = f"{first_name or ''} {last_name or ''}".strip()

                removed_users.append({
                    "user_id": str(user.id),
                    "user_name": user_name,
                    "previous_role": user.warehouse_role
                })

            return {
                "removed_users": removed_users,
                "warehouse_id": str(warehouse_id),
                "warehouse_name": warehouse.name,
                "total_removed": len(users)
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in remove multiple staff from warehouse: {str(e)}")
            raise e


