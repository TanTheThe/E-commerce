from datetime import datetime
from sqlmodel import and_
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.warehouse import WareHouseException
from src.schemas.warehouse import WarehouseCreateModel
import logging

logger = logging.getLogger(__name__)

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class CreateWareHouseService:
    async def create_warehouse(self, warehouse_data: WarehouseCreateModel, session: AsyncSession):
        try:
            condition_name = [Warehouse.name.ilike(warehouse_data.name)]
            existing_warehouse = await warehouse_repository.get_warehouse(session=session,
                                                                          where_conditions=condition_name)
            if existing_warehouse:
                WareHouseException.warehouse_already_exist()

            if warehouse_data.email or warehouse_data.phone:
                conditions = []
                if warehouse_data.email:
                    conditions.append(Warehouse.email.ilike(warehouse_data.email))
                if warehouse_data.phone:
                    conditions.append(Warehouse.phone == warehouse_data.phone)

                duplicate_check = await warehouse_repository.get_warehouse(session=session, where_conditions=conditions)
                if duplicate_check:
                    if duplicate_check.email == warehouse_data.email:
                        WareHouseException.email_already_use_in_another_warehouse()
                    if duplicate_check.phone == warehouse_data.phone:
                        WareHouseException.phone_already_use_in_another_warehouse()

            if warehouse_data.manager_id:
                condition_manager = [
                    User.id == warehouse_data.manager_id,
                    User.is_staff == True,
                    User.staff_status == "active"
                ]
                manager = await user_repository.get_user(session=session, where_conditions=condition_manager)
                if not manager:
                    AuthException.user_not_found()

                condition_manager_warehouse = [
                    Warehouse.manager_id == warehouse_data.manager_id,
                    Warehouse.is_active == True
                ]
                existing_managed = await warehouse_repository.get_warehouse(session=session,
                                                                            where_conditions=condition_manager_warehouse)

                if existing_managed:
                    WareHouseException.manager_was_at_warehouse(existing_managed)

            warehouse_code = await warehouse_repository.generate_warehouse_code(session)

            if warehouse_data.is_default:
                condition_default = [Warehouse.is_default == True]
                current_default = await warehouse_repository.get_warehouse(session=session,
                                                                           where_conditions=condition_default)

                if current_default:
                    condition_update_default = and_(Warehouse.id == current_default.id)
                    await warehouse_repository.update_warehouse(
                        condition_update_default,
                        {
                            "is_default": False,
                            "updated_at": datetime.now()
                        },
                        session
                    )

            warehouse_dict = warehouse_data.model_dump()
            warehouse_dict['code'] = warehouse_code

            new_warehouse = await warehouse_repository.create_warehouse(
                warehouse_dict, session
            )
            await session.commit()

            await session.refresh(new_warehouse)

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
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in create warehouse: {str(e)}")
            raise e
