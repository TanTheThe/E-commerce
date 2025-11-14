from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.authentication.utils import decode_url_safe_token
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.schemas.user import AdminStaffRole


user_repository = UserRepository()

class DetectUserRoleService:
    async def detect_user_role(self, email: str, allowed_roles: list[AdminStaffRole], session: AsyncSession):
        condition = [User.email == email, User.deleted_at.is_(None)]
        user = await user_repository.get_user(session=session, where_conditions=condition)

        if not user:
            AuthException.user_not_found()

        if not user.is_verified:
            AuthException.user_not_verified()

        detected_role = None

        if AdminStaffRole.ADMIN in allowed_roles and user.is_admin:
            detected_role = AdminStaffRole.ADMIN
        elif AdminStaffRole.STAFF in allowed_roles and user.is_staff:
            if user.staff_status != "active":
                AuthException.staff_account_disabled()
            detected_role = AdminStaffRole.STAFF

        if not detected_role:
            UserException.role_invalid()

        return detected_role

    async def detect_role_from_token(self, token: str, allowed_roles: list[AdminStaffRole], purpose: str, session: AsyncSession):
        token_data = None
        valid_token = False

        for role in allowed_roles:
            try:
                token_data = decode_url_safe_token(token, role.value, purpose=purpose)

                if token_data and token_data.get("email"):
                    valid_token = True
                    break

            except Exception:
                continue

        if not valid_token and not token_data:
            AuthException.token_invalid()

        email = token_data.get("email")

        condition = [User.email == email, User.deleted_at.is_(None)]
        user = await user_repository.get_user(session=session, where_conditions=condition)

        if not user:
            AuthException.user_not_found()

        if not user.is_verified:
            AuthException.user_not_verified()

        detected_role = None

        if AdminStaffRole.ADMIN in allowed_roles and user.is_admin:
            detected_role = AdminStaffRole.ADMIN
        elif AdminStaffRole.STAFF in allowed_roles and user.is_staff:
            if user.staff_status != "active":
                AuthException.staff_account_disabled()
            detected_role = AdminStaffRole.STAFF

        if not detected_role:
            UserException.role_invalid()

        return detected_role