from datetime import datetime

from sqlmodel import and_
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import WarehouseRole
from src.schemas.warehouse import AssignStaffToWarehouseModel

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class AssignStaffService:
    async def assign_staff_to_warehouse(self, warehouse_id: str, request: AssignStaffToWarehouseModel, session: AsyncSession):
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

        return {
            "user_id": str(user.id),
            "warehouse_id": str(warehouse_id),
            "warehouse_role": request.warehouse_role.value
        }


