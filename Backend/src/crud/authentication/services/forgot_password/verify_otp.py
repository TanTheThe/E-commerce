from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.authentication.services.forgot_password.forgot_password_security import ForgotPasswordSecurityService
from src.crud.authentication.utils import create_url_safe_token
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.schemas.user import VerifyOTPModel, UserRole
from fastapi import Request
import logging

user_repository = UserRepository()

logger = logging.getLogger(__name__)

forgot_password_security_service = ForgotPasswordSecurityService()

class VerifyOtpService:
    async def verify_otp(self, data: VerifyOTPModel, role: UserRole, session: AsyncSession, request: Request):
        email = data.email.strip().lower()
        otp = data.otp.strip()
        
        try:
            if not email or not otp:
                AuthException.invalid_otp_or_email()
                
            condition = [
                User.email == email,
                User.deleted_at.is_(None),
            ]
            user = await user_repository.get_user(session=session, where_conditions=condition)

            if not user:
                AuthException.invalid_otp_or_email()

            await self.validate_user_role(user, role)
            
            is_valid, error_message = await forgot_password_security_service.verify_otp(
                user_id=str(user.id),
                otp=otp
            )
            
            if not is_valid:
                if "hết hạn" in error_message.lower():
                    AuthException.otp_expired()
                elif "vượt" in error_message.lower():
                    AuthException.otp_max_attempts_exceeded()
                elif "còn lại" in error_message:
                    try:
                        attempts_left = int(error_message.split()[2])
                        AuthException.invalid_otp_attempts(attempts_left)
                    except:
                        AuthException.invalid_otp()
                else:
                    AuthException.invalid_otp()

            token_payload = {
                "email": user.email,
                "user_id": str(user.id),
                "timestamp": datetime.now().isoformat(),
            }

            token = create_url_safe_token(
                token_payload,
                role.value,
                purpose="reset_password"
            )

            return token
        
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            AuthException.otp_verification_failed()


    async def validate_user_role(self, user, role: UserRole):
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


