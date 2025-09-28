from starlette.responses import JSONResponse
from src.database.models import User
from src.errors.authentication import AuthException
from src.crud.authentication.utils import generate_password_hash, verify_password
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository
from fastapi import status

user_repository = UserRepository()


class ChangePasswordService:
    async def change_password(self, id: str, password_data, session: AsyncSession):
        condition = and_(User.id == id)
        user = await user_repository.get_user(condition, session)
        if not user:
            AuthException.user_not_found()

        password_valid = verify_password(password_data.old_password, user.password)

        if not password_valid:
            AuthException.invalid_password()

        new_password = password_data.new_password
        confirm_password = password_data.confirm_new_password

        if new_password != confirm_password:
            AuthException.password_mismatch()

        password_hash = generate_password_hash(new_password)
        await user_repository.update_user(user, {'password': password_hash}, session)
        await session.commit()

        return JSONResponse(content={
            "message": "Đổi mật khẩu thành công"
        }, status_code=status.HTTP_200_OK)
