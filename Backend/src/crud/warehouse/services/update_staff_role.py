from datetime import datetime
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.stock import WarehouseRole
from src.schemas.warehouse import UpdateStaffRoleModel
import logging

logger = logging.getLogger(__name__)

warehouse_repository = WareHouseRepository()
user_repository = UserRepository()

class UpdateStaffRoleService:
    async def update_staff_role(self, warehouse_id: str, user_id: str, request: UpdateStaffRoleModel, session: AsyncSession):
        try:
            condition_warehouse = [Warehouse.id == warehouse_id]
            warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition_warehouse)

            if not warehouse:
                raise WareHouseException.warehouse_not_found()

            condition_user = [User.id == user_id, User.deleted_at.is_(None)]
            user = await user_repository.get_user(session=session, where_conditions=condition_user)

            if not user:
                raise AuthException.user_not_found()

            if user.warehouse_id != warehouse_id:
                raise UserException.staff_not_in_this_warehouse()

            if request.warehouse_role == WarehouseRole.MANAGER.value:
                UserException.cant_assign_manager_in_this_function()

            if user.warehouse_role == request.warehouse_role.value:
                UserException.staff_already_in_this_role(request.warehouse_role.value)

            await user_repository.update_user(
                condition_user,
                {"warehouse_role": request.warehouse_role.value,
                 "updated_at": datetime.now()},
                session
            )

            await session.commit()
            await session.refresh(user)

            user_name = None
            first_name = user.first_name
            last_name = user.last_name
            if not first_name and not last_name:
                user_name = None
            user_name = f"{first_name or ''} {last_name or ''}".strip()

            return {
                "user_id": str(user.id),
                "user_name": user_name,
                "warehouse_id": str(warehouse_id),
                "warehouse_name": warehouse.name,
                "warehouse_role": request.warehouse_role.value,
                "updated_at": user.updated_at.isoformat()
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update warehouse: {str(e)}")
            raise e



