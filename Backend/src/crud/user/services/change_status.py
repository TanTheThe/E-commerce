from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.schemas.user import UserRole
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository
import logging

logger = logging.getLogger(__name__)

user_repository = UserRepository()
warehouse_repository = WareHouseRepository()


class ChangeStatusUserService:
    async def change_status_user(self, user_id: str, role: UserRole, session: AsyncSession):
        condition = [User.id == user_id, User.deleted_at.is_(None)]

        user_to_update = await user_repository.get_user(session=session, where_conditions=condition, for_update=True)

        if not user_to_update:
            AuthException.user_not_found()

        status_key = ""
        new_status = ""
        action = ""

        if role == UserRole.CUSTOMER:
            AuthException.unauthorized()

            current_status = user_to_update.customer_status
            new_status = "inactive" if current_status == "active" else "active"
            user_to_update.customer_status = new_status
            status_key = "customer_status"
            action = "chặn" if new_status == "inactive" else "mở chặn"

        elif role == UserRole.STAFF:
            AuthException.unauthorized()

            current_status = user_to_update.staff_status
            new_status = "inactive" if current_status == "active" else "active"
            user_to_update.staff_status = new_status
            status_key = "staff_status"
            action = "chặn" if new_status == "inactive" else "mở chặn"

        else:
            UserException.role_invalid()

        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed for update status: {str(e)}")
            UserException.update_status_failed()

        return {
            "id": str(user_to_update.id),
            "status_key": status_key,
            "status_value": new_status,
            "message": f"Đã {action} người dùng thành công"
        }

