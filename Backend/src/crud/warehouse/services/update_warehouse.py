from datetime import datetime
from typing import Optional

from sqlmodel import and_, or_
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import WarehouseRole
from src.schemas.warehouse import WarehouseUpdate
import logging

logger = logging.getLogger(__name__)

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class UpdateWarehouseService:
    async def update_warehouse(self, warehouse_id: str, warehouse_update: WarehouseUpdate, session: AsyncSession):
        try:
            if not warehouse_update.has_updates():
                WareHouseException.no_fields_updated()

            condition = [Warehouse.id == warehouse_id]
            existing_warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition,
                                                                          for_update=True)

            if not existing_warehouse:
                WareHouseException.warehouse_not_found()

            if warehouse_update.name and warehouse_update.name != existing_warehouse.name:
                condition_check_name = [Warehouse.name.ilike(warehouse_update.name)]
                duplicate_warehouse = await warehouse_repository.get_warehouse(session=session,
                                                                               where_conditions=condition_check_name)

                if duplicate_warehouse:
                    WareHouseException.warehouse_already_exist()

            if warehouse_update.email or warehouse_update.phone:
                await self.validate_contact_unique(warehouse_update.email, warehouse_update.phone, warehouse_id,
                                                   session)

            new_manager = None
            if warehouse_update.remove_manager:
                await self.remove_manager(existing_warehouse.manager_id, session)

            elif warehouse_update.manager_id is not None:
                if warehouse_update.manager_id != existing_warehouse.manager_id:
                    if existing_warehouse.manager_id:
                        await self.remove_manager(
                            existing_warehouse.manager_id,
                            session
                        )

                    new_manager = await self.assign_new_manager(
                        warehouse_update.manager_id,
                        warehouse_id,
                        session
                    )

            update_data = {}

            if warehouse_update.name is not None:
                update_data["name"] = warehouse_update.name

            if warehouse_update.address is not None:
                update_data["address"] = warehouse_update.address

            if warehouse_update.phone is not None:
                update_data["phone"] = warehouse_update.phone

            if warehouse_update.email is not None:
                update_data["email"] = warehouse_update.email

            if warehouse_update.remove_manager:
                update_data["manager_id"] = None
            elif warehouse_update.manager_id is not None:
                update_data["manager_id"] = warehouse_update.manager_id

            update_data["updated_at"] = datetime.now()

            await warehouse_repository.update_warehouse(
                and_(*condition),
                update_data,
                session
            )

            await session.commit()

            await session.refresh(existing_warehouse)

            manager_name = None
            if existing_warehouse.manager:
                first_name = existing_warehouse.manager.first_name
                last_name = existing_warehouse.manager.last_name
                if not first_name and not last_name:
                    manager_name = None
                manager_name = f"{first_name or ''} {last_name or ''}".strip()

            return {
                "id": str(existing_warehouse.id),
                "name": existing_warehouse.name,
                "code": existing_warehouse.code,
                "address": existing_warehouse.address,
                "phone": existing_warehouse.phone,
                "email": existing_warehouse.email,
                "manager_id": str(existing_warehouse.manager_id) if existing_warehouse.manager_id else None,
                "manager_name": manager_name,
                "is_active": existing_warehouse.is_active,
                "is_default": existing_warehouse.is_default,
                "updated_at": existing_warehouse.updated_at.isoformat()
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update warehouse: {str(e)}")
            raise e


    async def validate_contact_unique(self, email: Optional[str], phone: Optional[str],
                                      exclude_warehouse_id: str, session: AsyncSession) -> None:
        if not email and not phone:
            return

        conditions = [Warehouse.id != exclude_warehouse_id]

        if email and phone:
            conditions.append(
                or_(
                    Warehouse.email.ilike(email),
                    Warehouse.phone == phone
                )
            )
        elif email:
            conditions.append(Warehouse.email.ilike(email))
        elif phone:
            conditions.append(Warehouse.phone == phone)

        duplicate = await warehouse_repository.get_warehouse(session=session, where_conditions=conditions)

        if duplicate:
            if duplicate.email and duplicate.email.lower() == email.lower():
                WareHouseException.email_already_use_in_another_warehouse()
            if duplicate.phone == phone:
                WareHouseException.phone_already_use_in_another_warehouse()


    async def remove_manager(self, manager_id: Optional[str], session: AsyncSession) -> None:
        if not manager_id:
            return

        condition = [User.id == manager_id]
        await user_repository.update_user(
            condition,
            {
                "warehouse_id": None,
                "warehouse_role": None,
                "updated_at": datetime.now()
            },
            session
        )


    async def assign_new_manager(self, manager_id: str, warehouse_id: str, session: AsyncSession) -> User:
        condition_manager = [
            User.id == manager_id,
            User.is_staff == True,
            User.staff_status == "active",
            User.deleted_at.is_(None)
        ]

        manager = await user_repository.get_user(session=session, where_conditions=condition_manager)

        if not manager:
            raise AuthException.user_not_found()

        if manager.warehouse_id and manager.warehouse_role == WarehouseRole.MANAGER:
            condition_current_warehouse = [Warehouse.id == manager.warehouse_id]
            current_warehouse = await warehouse_repository.get_warehouse(session=session,
                                                                         where_conditions=condition_current_warehouse)

            if current_warehouse:
                WareHouseException.manager_was_at_warehouse(current_warehouse)

        await user_repository.update_user(
            condition_manager,
            {
                "warehouse_id": warehouse_id,
                "warehouse_role": WarehouseRole.MANAGER.value,
                "updated_at": datetime.now()
            },
            session
        )

        return manager






