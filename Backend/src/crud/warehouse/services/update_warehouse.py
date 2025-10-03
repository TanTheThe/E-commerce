from datetime import datetime
from sqlmodel import and_
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import WarehouseRole
from src.schemas.warehouse import WarehouseUpdate

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class UpdateWarehouseService:
    async def update_warehouse(self, warehouse_id: str, warehouse_update: WarehouseUpdate, session: AsyncSession):
        condition = and_(Warehouse.id == warehouse_id)
        existing_warehouse = await warehouse_repository.get_warehouse(condition, session)

        if not existing_warehouse:
            WareHouseException.warehouse_not_found()

        if warehouse_update.name and warehouse_update.name != existing_warehouse.name:
            condition_check_name = and_(Warehouse.name == warehouse_update.name)
            duplicate_warehouse = await warehouse_repository.get_warehouse(condition_check_name, session)

            if duplicate_warehouse:
                WareHouseException.warehouse_already_exist()

        if existing_warehouse.manager_id:
            condition_old_manager = and_(User.id == existing_warehouse.manager_id)
            await user_repository.update_user_some_field(
                condition_old_manager,
                {"warehouse_id": None, "warehouse_role": None},
                session
            )

        if warehouse_update.manager_id is not None:
            condition_manager = and_(
                User.id == warehouse_update.manager_id,
                User.is_staff == True,
                User.staff_status == "active"
            )
            manager = await user_repository.get_user(condition_manager, session)
            if not manager:
                AuthException.user_not_found()

            await user_repository.update_user_some_field(
                condition_manager,
                {"warehouse_id": warehouse_id, "warehouse_role": WarehouseRole.MANAGER},
                session
            )

        update_data = {
            "name": warehouse_update.name,
            "address": warehouse_update.address,
            "phone": warehouse_update.phone,
            "email": warehouse_update.email,
            "manager_id": warehouse_update.manager_id,
            "updated_at": datetime.now(),
        }

        await warehouse_repository.update_warehouse(condition, update_data, session)

        await session.commit()




