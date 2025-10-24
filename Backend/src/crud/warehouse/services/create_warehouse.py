from datetime import datetime
from sqlmodel import and_

from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.warehouse import WarehouseCreateModel

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class CreateWareHouseService:
    async def create_warehouse(self, warehouse_data: WarehouseCreateModel, session: AsyncSession):
        condition = and_(Warehouse.name == warehouse_data.name)
        existing_warehouse = await warehouse_repository.get_warehouse(condition, session)
        if existing_warehouse:
            WareHouseException.warehouse_already_exist()

        if warehouse_data.manager_id:
            condition_manager = and_(User.id == warehouse_data.manager_id, User.is_staff == True, User.staff_status == "active")
            manager = await user_repository.get_user(condition_manager, session)
            if not manager:
                AuthException.user_not_found()

        warehouse_code = await warehouse_repository.generate_warehouse_code(session)

        if warehouse_data.is_default:
            condition_default = and_(Warehouse.is_default == True)
            current_default = await warehouse_repository.get_warehouse(condition_default, session)

            if current_default:
                condition_update_default = and_(Warehouse.id == current_default.id)
                await warehouse_repository.update_warehouse(condition_update_default, {"is_default": False, "updated_at": datetime.now()}, session)

        warehouse_dict = warehouse_data.model_dump()
        warehouse_dict['code'] = warehouse_code

        new_warehouse = await warehouse_repository.create_warehouse(warehouse_dict, session)
        await session.commit()

        return {
            "id": str(new_warehouse.id),
            "name": new_warehouse.name,
            "code": new_warehouse.code,
            "address": new_warehouse.address,
            "phone": new_warehouse.phone,
            "email": new_warehouse.email,
            "manager_id": str(new_warehouse.manager_id),
            "is_active": new_warehouse.is_active,
            "is_default": new_warehouse.is_default,
            "created_at": str(new_warehouse.created_at),
        }

