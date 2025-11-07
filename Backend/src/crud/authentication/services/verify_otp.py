from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.authentication.utils import verify_password, create_url_safe_token
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.schemas.user import VerifyOTPModel, UserRole
from fastapi import Request

user_repository = UserRepository()

class VerifyOtpService:
    async def verify_otp(self, data: VerifyOTPModel, role: UserRole, session: AsyncSession, request: Request):
        try:
            email = data.email
            otp = data.otp

            condition = [
                User.email == email,
                User.deleted_at.is_(None),
            ]
            user = await user_repository.get_user(session=session, where_conditions=condition)

            if not user or not user.otp_hash:
                AuthException.invalid_otp_or_email()

            if user.otp_attempts >= 5:
                AuthException.otp_max_attempts_exceeded()

            await self.validate_user_role(user, role)

            if not user.expires_at or datetime.now() > user.expires_at:
                AuthException.otp_expired()

            if not verify_password(otp, user.otp_hash):
                update_data = {
                    "otp_attempts": user.otp_attempts + 1,
                    "updated_at": datetime.now(),
                }
                condition_update = [
                    User.id == user.id,
                    User.email == user.email,
                    User.deleted_at.is_(None),
                ]
                await user_repository.update_user(condition_update, update_data, session=session)
                await session.commit()

                attempts_left = 5 - user.otp_attempts - 1

                AuthException.invalid_otp_attempts(attempts_left)

            update_data = {
                "otp_hash": None,
                "expires_at": None,
                "otp_attempts": 0,
                "updated_at": datetime.now(),
            }
            condition_update = [
                User.id == user.id,
                User.email == user.email,
                User.deleted_at.is_(None),
            ]
            await user_repository.update_user(condition_update, update_data, session=session)
            await session.commit()

            token_payload = {
                "email": user.email,
                "user_id": str(user.id),
                "timestamp": datetime.now().isoformat(),
            }

            token = create_url_safe_token(token_payload, role, "reset_password")

            return token
        except Exception as e:
            await session.rollback()
            AuthException.verification_failed()


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


