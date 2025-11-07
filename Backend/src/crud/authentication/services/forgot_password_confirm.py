from datetime import datetime
from itsdangerous import SignatureExpired, BadSignature
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.authentication.services.token_blacklist_service import TokenBlacklistService
from src.crud.authentication.utils import decode_url_safe_token, verify_password, generate_password_hash
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.schemas.user import ForgotPasswordConfirmModel, UserRole
from fastapi import Request

user_repository = UserRepository()
token_blacklist_service = TokenBlacklistService()

class ForgotPasswordConfirmService:
    async def forgot_password_confirm(self, data: ForgotPasswordConfirmModel, role: UserRole, session: AsyncSession, request: Request):
        try:
            token_data = decode_url_safe_token(
                data.token,
                role.value,
                purpose="reset_password",
            )

            is_blacklisted = await token_blacklist_service.token_in_blocklist(
                token=data.token,
                role=role.value,
                purpose="reset_password",
                request=request
            )

            if is_blacklisted:
                AuthException.token_already_used()

            user_email = token_data.get("email")
            user_id = token_data.get("user_id")

            if not user_email:
                AuthException.token_invalid()

            condition = [
                User.email == user_email, User.deleted_at.is_(None)
            ]
            user = await user_repository.get_user(session=session, where_conditions=condition)

            if not user:
                AuthException.user_not_found()

            if user_id and str(user.id) != user_id:
                AuthException.token_invalid()

            self.validate_user_role(user, role)

            if data.new_password != data.new_password_confirm:
                AuthException.password_mismatch()

            self.validate_password_strength(data.new_password)

            if verify_password(data.new_password, user.password):
                AuthException.same_password_error()

            password_hash = generate_password_hash(data.new_password)

            update_data = {
                "password": password_hash,
                'otp': None,
                'expires_at': None,
                'updated_at': datetime.now()
            }

            await user_repository.update_user(condition, update_data, session)

            await token_blacklist_service.add_token_to_blocklist(
                token=data.token,
                role=role.value,
                purpose="reset_password",
                request=request,
                ttl=None,
                metadata={
                    "user_id": str(user.id),
                    "email": user.email,
                    "role": role.value,
                    "action": "password_reset_success"
                }
            )

            await session.commit()

            role_display = self.get_role_display(role)

            return f"Đổi mật khẩu {role_display} thành công"

        except SignatureExpired:
            AuthException.token_invalid()
        except BadSignature:
            AuthException.token_invalid()
        except Exception as e:
            await session.rollback()
            raise


    def validate_user_role(self, user, role: UserRole):
        if role == UserRole.ADMIN and not user.is_admin:
            AuthException.unauthorized_admin()
        elif role == UserRole.STAFF and not user.is_staff:
            AuthException.unauthorized_staff()
        elif role == UserRole.CUSTOMER and not user.is_customer:
            AuthException.unauthorized_customer()

        if role == UserRole.STAFF and user.staff_status != "active":
            AuthException.staff_account_disabled()
        elif role == UserRole.CUSTOMER and user.customer_status != "active":
            AuthException.customer_account_disabled()

        if user.deleted_at is not None:
            AuthException.account_deleted()


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


    def get_role_display(self, role: UserRole) -> str:
        role_mapping = {
            UserRole.ADMIN: "quản trị viên",
            UserRole.STAFF: "nhân viên",
            UserRole.CUSTOMER: "khách hàng"
        }
        return role_mapping.get(role, "người dùng")
