import logging
from datetime import timedelta, datetime
import pyotp
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.authentication.services.login_2fa.verify_login_security import VerifyLoginSecurityService
from src.crud.authentication.services.logout.token_blacklist_service import TokenBlacklistService
from src.crud.authentication.utils import decode_url_safe_token, create_access_token
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.schemas.user import VerifyLoginAdminModel, AdminStaffRole
from fastapi import Request

logger = logging.getLogger(__name__)

REFRESH_TOKEN_EXPIRY = 2

token_blacklist_service = TokenBlacklistService()
verify_login_security_service = VerifyLoginSecurityService()
user_repository = UserRepository()

class VerifyLoginService:
    async def verify_login(self, user_data: VerifyLoginAdminModel, role: AdminStaffRole, request: Request, session: AsyncSession):
        token = user_data.token
        otp = user_data.otp

        is_blacklisted = await token_blacklist_service.token_in_blocklist(
            token=token,
            role=role.value,
            purpose="first_class_login",
        )

        if is_blacklisted:
            AuthException.token_already_used()

        token_data = decode_url_safe_token(
            token=token,
            role=role.value,
            purpose="first_class_login",
        )

        user_id = token_data.get('id')
        if not user_id:
            AuthException.token_invalid()

        await verify_login_security_service.check_otp_rate_limit(user_id, session)

        condition = [User.id == user_id, User.deleted_at.is_(None)]
        user = await user_repository.get_user(session=session, where_conditions=condition)
        if not user:
            await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
            AuthException.user_not_found()

        token_email = token_data.get('email')
        if not token_email:
            await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
            AuthException.token_invalid()

        if not user.is_verified:
            await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
            AuthException.user_not_verified()

        if role == AdminStaffRole.ADMIN:
            if not user.is_admin:
                await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
                AuthException.unauthorized_admin()
        elif role == AdminStaffRole.STAFF:
            if not user.is_staff:
                await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
                AuthException.unauthorized_staff()
            if user.staff_status != "active":
                await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
                AuthException.staff_account_disabled()

        if not user.two_fa_secret or not user.two_fa_enabled:
            await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
            AuthException.two_fa_not_setup()

        try:
            totp = pyotp.TOTP(user.two_fa_secret)

            if not totp.verify(otp, valid_window=1):
                await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
                AuthException.invalid_otp()

        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            await verify_login_security_service.log_otp_attempt(user_id, False, request, session)
            AuthException.invalid_otp()

        await verify_login_security_service.log_otp_attempt(user_id, True, request, session)

        await token_blacklist_service.add_token_to_blocklist(
            token=token,
            role=role.value,
            purpose="first_class_login",
            metadata={
                "user_id": str(user.id),
                "action": "otp_verified"
            }
        )

        user_payload = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "id": str(user.id),
            "email": user.email
        }

        if role == AdminStaffRole.STAFF:
            user_payload["staff_status"] = user.staff_status

        access_token = create_access_token(
            user_data=user_payload,
            role=str(role.value),
        )

        refresh_token = create_access_token(
            user_data=user_payload,
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            role=str(role.value),
        )

        await user_repository.update_user(
            condition,
            {
                "updated_at": datetime.now()
            },
            session
        )

        role_display = "quản trị viên" if role == AdminStaffRole.ADMIN else "nhân viên"

        return {
            "message": f"Đăng nhập {role_display} thành công",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_payload,
                "role": role.value
            }
        }




