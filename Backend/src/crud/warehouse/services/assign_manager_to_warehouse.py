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

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class AssignManagerService:
    async def assign_manager_to_warehouse(self, warehouse_id: str, user_id: str,
                                          new_role_for_old_manager: WarehouseRole,
                                          session: AsyncSession):
        if new_role_for_old_manager == WarehouseRole.MANAGER:
            UserException.new_role_for_old_manager()

        condition_warehouse = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        condition_user = and_(User.id == user_id, User.deleted_at.is_(None))
        user = await user_repository.get_user(condition_user, session)
        if not user:
            AuthException.user_not_found()

        if not user.is_staff:
            UserException.only_staff_can_be_assigned()

        if user.staff_status != "active":
            UserException.only_staff_active_can_be_assigned()

        if warehouse.manager_id:
            old_manager_condition = and_(User.id == warehouse.manager_id)
            await user_repository.update_user_some_field(
                old_manager_condition,
                {
                    "warehouse_role": new_role_for_old_manager.value,
                    "updated_at": datetime.now()
                },
                session
            )

        await warehouse_repository.update_warehouse(
            condition_warehouse,
            {
                "manager_id": user.id,
                "updated_at": datetime.now()
            },
            session
        )

        await user_repository.update_user_some_field(
            condition_user,
            {
                "warehouse_role": WarehouseRole.MANAGER.value,
                "warehouse_id": warehouse_id,
                "updated_at": datetime.now()
            },
            session
        )

        await session.commit()


