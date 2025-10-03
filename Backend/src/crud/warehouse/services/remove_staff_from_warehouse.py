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


warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class RemoveStaffService:
    async def remove_staff_from_warehouse(self, warehouse_id: str, user_id: str, session: AsyncSession):
        condition_warehouse = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        condition_user = and_(User.id == user_id, User.deleted_at.is_(None))
        user = await user_repository.get_user(condition_user, session)
        if not user:
            AuthException.user_not_found()

        if str(user.warehouse_id) != warehouse_id:
            UserException.staff_not_in_this_warehouse()

        if user.warehouse_role == "manager":
            UserException.cant_remove_manager_in_this_function()

        await user_repository.update_user_some_field(condition_user, {"warehouse_id": None,
                                                                      "warehouse_role": None,
                                                                      "updated_at": datetime.now()},
                                                     session)
        await session.commit()

        return {
            "user_id": str(user.id),
            "warehouse_id": str(warehouse_id),
            "warehouse_role": None
        }


    async def remove_multiple_staff_from_warehouse(self, warehouse_id: str, user_ids: List[str], session: AsyncSession):
        condition_warehouse = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        condition_users = [User.id.in_(user_ids), User.deleted_at.is_(None), User.is_staff == True]
        users, _ = await user_repository.get_all_users(condition_users, session, 0, 1000)

        if len(users) != len(user_ids):
            found_ids = {str(user.id) for user in users}
            missing_ids = set(user_ids) - found_ids
            UserException.one_staff_doesnt_exist()

        for user in users:
            if str(user.warehouse_id) != warehouse_id:
                UserException.staff_not_in_this_warehouse()

            if user.warehouse_role == "manager":
                UserException.cant_remove_manager_in_this_function()

        condition_remove = User.id.in_(user_ids)
        await user_repository.update_user_some_field(
            condition_remove,
            {
                "warehouse_id": None,
                "warehouse_role": None,
                "updated_at": datetime.now()
            },
            session
        )

        await session.commit()

        return {
            "removed_users": [
                {
                    "user_id": str(user.id),
                    "warehouse_id": str(warehouse_id),
                    "warehouse_role": None
                }
                for user in users
            ],
            "warehouse_id": str(warehouse_id),
            "total_removed": len(users)
        }


