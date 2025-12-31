from datetime import datetime
from typing import Optional
from sqlmodel import and_
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import WarehouseRole
import logging

logger = logging.getLogger(__name__)

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class AssignManagerService:
    async def assign_manager_to_warehouse(self, warehouse_id: str, user_id: str,
                                          new_role_for_old_manager: Optional[WarehouseRole],
                                          session: AsyncSession):
        try:
            condition_warehouse = [Warehouse.id == warehouse_id]
            warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition_warehouse)
            if not warehouse:
                WareHouseException.warehouse_not_found()

            if not warehouse.is_active:
                raise WareHouseException.cant_assign_to_inactive_warehouse()

            new_manager = await self.validate_new_manager(user_id, warehouse_id, session)

            old_manager_id = None
            old_manager_new_role = None

            if warehouse.manager_id:
                if warehouse.manager_id == user_id:
                    WareHouseException.already_managed_this_warehouse()

                if new_role_for_old_manager is None:
                    UserException.new_role_for_old_manager_required()

                old_manager_id = warehouse.manager_id
                old_manager_new_role = new_role_for_old_manager.value

                await self.demote_old_manager(
                    warehouse.manager_id,
                    new_role_for_old_manager,
                    warehouse_id,
                    session
                )
            else:
                if new_role_for_old_manager is not None:
                    UserException.warehouse_has_no_manager()

            await self.promote_new_manager(user_id, warehouse_id, session)

            await warehouse_repository.update_warehouse(
                and_(*condition_warehouse),
                {
                    "manager_id": user_id,
                    "updated_at": datetime.now()
                },
                session
            )

            await session.commit()

            await session.refresh(warehouse)
            await session.refresh(new_manager)

            new_manager_name = None
            first_name = new_manager.first_name
            last_name = new_manager.last_name
            if not first_name and not last_name:
                new_manager_name = None
            new_manager_name = f"{first_name or ''} {last_name or ''}".strip()

            return {
                "new_manager_id": str(new_manager.id),
                "new_manager_name": new_manager_name,
                "warehouse_id": str(warehouse.id),
                "warehouse_name": warehouse.name,
                "old_manager_id": str(old_manager_id) if old_manager_id else None,
                "old_manager_new_role": old_manager_new_role
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update warehouse: {str(e)}")
            raise e


    async def validate_new_manager(self, user_id: str, warehouse_id: str, session: AsyncSession) -> User:
        condition = [User.id == user_id, User.deleted_at.is_(None)]
        user = await user_repository.get_user(session=session, where_conditions=condition)

        if not user:
            raise AuthException.user_not_found()

        if not user.is_staff:
            raise UserException.only_staff_can_be_assigned()

        if user.staff_status != "active":
            raise UserException.only_staff_active_can_be_assigned()

        if (user.warehouse_id and
                user.warehouse_id != warehouse_id and
                user.warehouse_role == WarehouseRole.MANAGER.value):

            condition_warehouse = [Warehouse.id == user.warehouse_id]
            other_warehouse = await warehouse_repository.get_warehouse(
                session=session,
                where_conditions=condition_warehouse
            )

            WareHouseException.managing_different_warehouse(other_warehouse)

        return user

    async def demote_old_manager(self, old_manager_id: str, new_role: WarehouseRole, warehouse_id: str,
                                 session: AsyncSession) -> None:
        condition = [User.id == old_manager_id, User.deleted_at.is_(None)]

        update_data = {
            "warehouse_role": new_role.value,
            "warehouse_id": warehouse_id,
            "updated_at": datetime.now()
        }

        await user_repository.update_user(
            condition,
            update_data,
            session
        )

    async def promote_new_manager(self, user_id: str, warehouse_id: str, session: AsyncSession) -> None:
        condition = [User.id == user_id, User.deleted_at.is_(None)]

        update_data = {
            "warehouse_role": WarehouseRole.MANAGER.value,
            "warehouse_id": warehouse_id,
            "updated_at": datetime.now()
        }

        await user_repository.update_user(
            condition,
            update_data,
            session
        )


