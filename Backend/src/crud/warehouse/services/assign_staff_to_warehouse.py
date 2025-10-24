from datetime import datetime
from sqlmodel import and_, case
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import WarehouseRole
from src.schemas.warehouse import AssignStaffItemModel, AssignMultipleStaffModel

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class AssignStaffService:
    async def assign_staff_to_warehouse(self, warehouse_id: str, request: AssignStaffItemModel, session: AsyncSession):
        condition_warehouse = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        if not warehouse.is_active:
            WareHouseException.cant_assign_to_inactive_warehouse()

        condition_user = and_(User.id == request.user_id, User.deleted_at.is_(None))
        user = await user_repository.get_user(condition_user, session)
        if not user:
            AuthException.user_not_found()

        if not user.is_staff:
            UserException.only_staff_can_be_assigned()

        if user.staff_status != "active":
            UserException.only_staff_active_can_be_assigned()

        if request.warehouse_role == WarehouseRole.MANAGER:
            UserException.cant_assign_manager_in_this_function()

        if user.warehouse_id and user.warehouse_id != warehouse_id:
            UserException.staff_has_been_assigned_to_another_warehouse()

        if user.warehouse_id == warehouse_id:
            UserException.staff_already_in_this_warehouse(user.warehouse_role)

        await user_repository.update_user_some_field(condition_user, {"warehouse_id": warehouse_id,
                                                                      "warehouse_role": request.warehouse_role.value,
                                                                      "updated_at": datetime.now()},
                                                     session)

        await session.commit()

        return {
            "user_id": str(user.id),
            "warehouse_id": str(warehouse_id),
            "warehouse_role": request.warehouse_role.value
        }

    async def assign_multiple_staff_to_warehouse(self, warehouse_id: str,
                                                 request: AssignMultipleStaffModel,
                                                 session: AsyncSession):
        condition_warehouse = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        if not warehouse.is_active:
            WareHouseException.cant_assign_to_inactive_warehouse()

        user_ids = [staff.user_id for staff in request.staff_list]

        condition_users = [User.id.in_(user_ids),
            User.deleted_at.is_(None),
            User.is_staff == True
        ]
        users, _ = await user_repository.get_all_users(condition_users, session, 0, 1000)

        if len(users) != len(user_ids):
            found_ids = {str(user.id) for user in users}
            missing_ids = set(user_ids) - found_ids
            UserException.one_staff_doesnt_exist()

        role_mapping = {staff.user_id: staff.warehouse_role for staff in request.staff_list}

        for user in users:
            if not user.is_staff:
                UserException.only_staff_can_be_assigned()

            if user.staff_status != "active":
                UserException.only_staff_active_can_be_assigned()

            requested_role = role_mapping[str(user.id)]
            if requested_role == WarehouseRole.MANAGER:
                UserException.cant_assign_manager_in_this_function()

            if user.warehouse_id and user.warehouse_id != warehouse_id:
                UserException.staff_has_been_assigned_to_another_warehouse()

            if user.warehouse_id == warehouse_id:
                UserException.staff_already_in_this_warehouse(user.warehouse_role)

        role_case = case(
            *[(User.id == user_id, role.value) for user_id, role in role_mapping.items()],
            else_=User.warehouse_role
        )

        condition_assign = User.id.in_(user_ids)
        await user_repository.update_user_some_field(
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
                    "user_id": user_id,
                    "warehouse_id": str(warehouse_id),
                    "warehouse_role": role.value
                }
                for user_id, role in role_mapping.items()
            ],
            "warehouse_id": str(warehouse_id),
            "total_assigned": len(user_ids)
        }


