from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Request
from src.crud.authentication.services.login_security.login_attempt_logger import AttemptLoggerService
from src.crud.authentication.services.login_security.login_security import LoginSecurityService
from src.crud.authentication.utils import verify_password, create_url_safe_token
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.schemas.user import AdminStaffRole, UserLoginModel
import logging

user_repository = UserRepository()
login_security_service = LoginSecurityService()
attempt_logger_service = AttemptLoggerService()

logger = logging.getLogger(__name__)

class LoginAdminStaffService:
    async def login_admin_staff(self, user_data: UserLoginModel, role: AdminStaffRole, request: Request, session: AsyncSession):
        email = user_data.email
        password = user_data.password

        try:
            await login_security_service.check_rate_limit(email, request, session)

            condition = [User.email == email, User.deleted_at.is_(None)]
            user = await user_repository.get_user(session=session, where_conditions=condition)

            if not user:
                await login_security_service.handle_failed_login(email, request, session)
                AuthException.user_not_found()

            password_valid = verify_password(password, user.password)
            if not password_valid:
                await login_security_service.handle_failed_login(email, request, session)
                AuthException.invalid_account()

            if not user.is_verified:
                await login_security_service.handle_failed_login(email, request, session)
                AuthException.user_not_verified()

            if role == AdminStaffRole.ADMIN:
                if not user.is_admin:
                    await login_security_service.handle_failed_login(email, request, session)
                    AuthException.unauthorized_admin()
            elif role == AdminStaffRole.STAFF:
                if not user.is_staff:
                    await login_security_service.handle_failed_login(email, request, session)
                    AuthException.unauthorized_staff()
                if user.staff_status != "active":
                    await login_security_service.handle_failed_login(email, request, session)
                    AuthException.staff_account_disabled()

            token = create_url_safe_token(
                {"id": str(user.id), "email": user.email},
                role=str(role.value),
                purpose='first_class_login'
            )

            role_display = "quản trị viên" if role == AdminStaffRole.ADMIN else "nhân viên"
            
            await login_security_service.handle_successful_login(email, request, session)

            if not user.two_fa_secret or not user.two_fa_enabled:
                return {
                        "message": f"Lần đăng nhập {role_display} đầu tiên, vui lòng thiết lập 2FA",
                        "data": {
                            "isFirstLogin": True,
                            "token": token,
                            "requiresSetup": True,
                            "role": role.value
                        }
                    }
            else:
                return {
                        "message": f"Vui lòng nhập mã OTP để tiếp tục đăng nhập {role_display}",
                        "data": {
                            "isFirstLogin": False,
                            "token": token,
                            "requiresSetup": False,
                            "role": role.value
                        }
                    }

        except Exception as e:
            logger.error(f"Login failed for {email}: {str(e)}")
            AuthException.login_failed()