from datetime import datetime
from typing import List, Dict
from sqlmodel import case
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import WarehouseRole
from src.schemas.warehouse import AssignStaffItemModel, AssignMultipleStaffModel
import logging

logger = logging.getLogger(__name__)

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class AssignStaffService:
    async def assign_staff_to_warehouse(self, warehouse_id: str, request: AssignStaffItemModel, session: AsyncSession):
        try:
            condition_warehouse = [Warehouse.id == warehouse_id]
            warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition_warehouse)
            if not warehouse:
                WareHouseException.warehouse_not_found()

            if not warehouse.is_active:
                WareHouseException.cant_assign_to_inactive_warehouse()

            condition_user = [User.id == request.user_id, User.deleted_at.is_(None)]
            user = await user_repository.get_user(session=session, where_conditions=condition_user)
            if not user:
                AuthException.user_not_found()

            self.validate_user_conditions(user, warehouse_id, request.warehouse_role)

            await user_repository.update_user(condition_user,
                                              {"warehouse_id": warehouse_id,
                                               "warehouse_role": request.warehouse_role.value,
                                               "updated_at": datetime.now()},
                                              session)

            await session.commit()

            await session.refresh(user)

            return {
                "user_id": str(user.id),
                "warehouse_id": str(warehouse_id),
                "warehouse_role": request.warehouse_role.value,
                "warehouse_name": warehouse.name,
                "assigned_at": datetime.now().isoformat()
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in assign staff to warehouse: {str(e)}")
            raise e


    async def assign_multiple_staff_to_warehouse(self, warehouse_id: str, request: AssignMultipleStaffModel,
                                                 session: AsyncSession):
        try:
            condition_warehouse = [Warehouse.id == warehouse_id]
            warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition_warehouse)
            if not warehouse:
                WareHouseException.warehouse_not_found()

            if not warehouse.is_active:
                WareHouseException.cant_assign_to_inactive_warehouse()

            user_ids = [str(staff.user_id) for staff in request.staff_list]
            role_mapping = {
                str(staff.user_id): staff.warehouse_role
                for staff in request.staff_list
            }

            users = await self.validate_multiple_users(
                user_ids,
                warehouse_id,
                role_mapping,
                session
            )

            role_case = case(
                *[
                    (User.id == user_id, role.value)
                    for user_id, role in role_mapping.items()
                ],
                else_=User.warehouse_role
            )

            condition_assign = [
                User.id.in_(user_ids),
                User.deleted_at.is_(None)
            ]
            await user_repository.update_user(
                condition_assign,
                {
                    "warehouse_id": warehouse_id,
                    "warehouse_role": role_case,
                    "updated_at": datetime.now()
                },
                session
            )

            await session.commit()

            return {
                "assigned_users": [
                    {
                        "user_id": str(user_id),
                        "warehouse_id": str(warehouse_id),
                        "warehouse_role": role.value
                    }
                    for user_id, role in role_mapping.items()
                ],
                "warehouse_id": str(warehouse_id),
                "warehouse_name": warehouse.name,
                "total_assigned": len(user_ids)
            }
        except Exception as e:
            logger.error(f"Error in assign staff to warehouse: {str(e)}")
            await session.rollback()
            raise e


    def validate_user_conditions(self, user: User, warehouse_id: str, warehouse_role: WarehouseRole) -> None:
        if not user.is_staff:
            raise UserException.only_staff_can_be_assigned()

        if user.staff_status != "active":
            raise UserException.only_staff_active_can_be_assigned()

        if warehouse_role == WarehouseRole.MANAGER:
            raise UserException.cant_assign_manager_in_this_function()

        if user.warehouse_id and user.warehouse_id != warehouse_id:
            raise UserException.staff_has_been_assigned_to_another_warehouse()

        if user.warehouse_id == warehouse_id:
            raise UserException.staff_already_in_this_warehouse(
                role=user.warehouse_role
            )


    async def validate_multiple_users(self, user_ids: List[str], warehouse_id: str,
                                      role_mapping: Dict[str, WarehouseRole], session: AsyncSession) -> List[User]:
        condition_users = [
            User.id.in_(user_ids),
            User.deleted_at.is_(None),
            User.is_staff == True
        ]
        users, _ = await user_repository.get_all_users(session=session, where_conditions=condition_users, skip=0,
                                                       limit=len(user_ids) + 10)

        if len(users) != len(user_ids):
            UserException.one_staff_doesnt_exist()

        validation_errors = []
        for user in users:
            try:
                requested_role = role_mapping[user.id]
                self.validate_user_conditions(user, warehouse_id, requested_role)
            except Exception as e:
                validation_errors.append({
                    "user_id": str(user.id),
                    "error": str(e)
                })

        if validation_errors:
            WareHouseException.some_staff_invalid()

        return users


