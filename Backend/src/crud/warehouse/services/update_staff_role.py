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
from src.schemas.warehouse import UpdateStaffRoleModel

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class UpdateStaffRoleService:
    async def update_staff_role(self, warehouse_id: str, user_id: str, request: UpdateStaffRoleModel, session: AsyncSession):
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

        if request.warehouse_role == WarehouseRole.MANAGER:
            UserException.cant_assign_manager_in_this_function()

        if user.warehouse_role == request.warehouse_role.value:
            UserException.staff_already_in_this_role(request.warehouse_role.value)

        await user_repository.update_user_some_field(condition_user, {"warehouse_role": request.warehouse_role.value,
                                                                      "updated_at": datetime.now()},
                                                     session)

        await session.commit()

        return {
            "user_id": str(user.id),
            "warehouse_id": str(warehouse_id),
            "warehouse_role": request.warehouse_role.value
        }


