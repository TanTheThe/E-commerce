from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository

user_repository = UserRepository()
warehouse_repository = WareHouseRepository()


class UpdateProfileService:
    async def update_profile(self, user_id: str, update_data, session: AsyncSession):
        conditions = [
            User.id == user_id,
            User.deleted_at.is_(None)
        ]
        user_need_update = await user_repository.get_user(session=session, where_conditions=conditions)

        if not user_need_update:
            AuthException.user_not_found()

        update_dict = update_data.model_dump(exclude_none=True)

        if not update_dict:
            raise ValueError("Không có dữ liệu để cập nhật")

        if 'phone' in update_dict and update_dict['phone'] != user_need_update.phone:
            conditions = [
                User.phone == update_dict['phone'],
                User.id != user_id,
                User.deleted_at.is_(None)
            ]
            _, count = await user_repository.get_all_users(session=session, where_conditions=conditions)
            if count > 0:
                UserException.phone_already_in_use()

        user_after_update = await user_repository.update_user(
            user_need_update,
            update_dict,
            session
        )

        await session.commit()
        await session.refresh(user_after_update)

        return user_after_update

