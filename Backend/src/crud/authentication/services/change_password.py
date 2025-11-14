from datetime import datetime
from src.crud.authentication.utils import verify_password, generate_password_hash
from src.database.models import User
from src.errors.authentication import AuthException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository
from fastapi import HTTPException
from src.schemas.user import ChangePasswordModel, UserRole
import logging

user_repository = UserRepository()

logger = logging.getLogger(__name__)

class ChangePasswordService:
    async def change_password(self, user_id: str, password_data: ChangePasswordModel, role: UserRole, session: AsyncSession):
        try:
            self.validate_input(password_data)

            user = await self.find_and_validate_user(user_id, role, session)

            await self.verify_old_password(password_data.old_password, user)

            await self.validate_new_password(password_data, user)

            await self.update_user_password(user, password_data.new_password, session)

            await session.commit()

            role_display = self.get_role_display(role)

            return {
                "role_display": role_display,
                "data": {
                    "user_id": str(user.id),
                    "email": user.email,
                    "updated_at": datetime.now().isoformat()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error("Error change password: ", e)
            AuthException.password_change_failed()


    def validate_input(self, password_data: ChangePasswordModel):
        if not password_data.old_password or len(password_data.old_password.strip()) == 0:
            AuthException.old_password_required()

        if not password_data.new_password or len(password_data.new_password.strip()) == 0:
            AuthException.new_password_required()

        if not password_data.confirm_new_password or len(password_data.confirm_new_password.strip()) == 0:
            AuthException.confirm_password_required()


    async def find_and_validate_user(self, user_id: str, role: UserRole, session: AsyncSession):
        condition = [User.id == user_id, User.deleted_at.is_(None)]
        user = await user_repository.get_user(session=session, where_conditions=condition)

        if not user:
            AuthException.user_not_found()

        if not user.is_verified:
            AuthException.user_not_verified()

        if role == UserRole.ADMIN:
            if not user.is_admin:
                AuthException.unauthorized_admin()
        elif role == UserRole.STAFF:
            if not user.is_staff:
                AuthException.unauthorized_staff()
            if user.staff_status != "active":
                AuthException.staff_account_disabled()
        elif role == UserRole.CUSTOMER:
            if not user.is_customer:
                AuthException.unauthorized_customer()
            if user.customer_status != "active":
                AuthException.customer_account_disabled()

        if user.deleted_at is not None:
            AuthException.account_deleted()

        return user


    async def verify_old_password(self, old_password: str, user):
        password_valid = verify_password(old_password, user.password)

        if not password_valid:
            AuthException.invalid_password()


    async def validate_new_password(self, password_data: ChangePasswordModel, user):
        new_password = password_data.new_password
        confirm_password = password_data.confirm_new_password

        if new_password != confirm_password:
            AuthException.password_mismatch()

        self.validate_password_strength(new_password)

        if verify_password(new_password, user.password):
            AuthException.same_password_error()

    def validate_password_strength(self, password: str):
        if len(password) < 8:
            AuthException.password_too_short()

        if len(password) > 100:
            AuthException.password_too_long()

        if not any(c.isupper() for c in password):
            AuthException.password_missing_uppercase()

        if not any(c.islower() for c in password):
            AuthException.password_missing_lowercase()

        if not any(c.isdigit() for c in password):
            AuthException.password_missing_digit()

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            AuthException.password_missing_special_char()

        common_patterns = [
            r'12345', r'password', r'qwerty', r'abc123',
            r'111111', r'123123', r'admin', r'letmein'
        ]
        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                AuthException.password_contains_common_pattern()

        if self.has_excessive_repeated_chars(password):
            AuthException.password_too_repetitive()

    def has_excessive_repeated_chars(self, password: str, max_repeat: int = 5) -> bool:
        for i in range(len(password) - max_repeat + 1):
            if len(set(password[i:i + max_repeat])) == 1:
                return True
        return False


    async def update_user_password(self, user, new_password: str, session: AsyncSession):
        try:
            password_hash = generate_password_hash(new_password)

            update_data = {
                'password': password_hash,
                'updated_at': datetime.now()
            }

            condition = [User.id == user.id, User.deleted_at.is_(None)]
            await user_repository.update_user(condition, update_data, session)

        except Exception as e:
            logger.error("Error update user password: ", e)
            raise


    def get_role_display(self, role: UserRole) -> str:
        role_mapping = {
            UserRole.ADMIN: "quản trị viên",
            UserRole.STAFF: "nhân viên",
            UserRole.CUSTOMER: "khách hàng"
        }
        return role_mapping.get(role, "người dùng")
