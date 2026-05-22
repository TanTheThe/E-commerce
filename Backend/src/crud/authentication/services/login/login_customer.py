from datetime import timedelta, datetime
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.authentication.services.login_security.login_security import LoginSecurityService
from src.crud.authentication.utils import verify_password, create_access_token
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.schemas.user import UserLoginModel
import logging

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
REFRESH_TOKEN_EXPIRY = 7

user_repository = UserRepository()
login_security_service = LoginSecurityService()

logger = logging.getLogger(__name__)

class LoginCustomerService:
    async def login_customer(self, user_data: UserLoginModel, request: Request, session: AsyncSession):
        email = user_data.email
        password = user_data.password

        try:
            await login_security_service.check_rate_limit(email, request, session)

            condition = [
                User.email == email,
                User.deleted_at.is_(None),
            ]

            user = await user_repository.get_user(session=session, where_conditions=condition)

            if not user:
                await login_security_service.handle_failed_login(email, request, session)
                AuthException.user_not_found()

            if not user.is_verified:
                await login_security_service.handle_failed_login(email, request, session)
                AuthException.user_not_verified()

            if user.customer_status != "active":
                await login_security_service.handle_failed_login(email, request, session)
                AuthException.customer_account_disabled()

            if not user.is_customer:
                await login_security_service.handle_failed_login(email, request, session)
                AuthException.unauthorized_customer()

            password_valid = verify_password(password, user.password)

            if not password_valid:
                await login_security_service.handle_failed_login(email, request, session)
                AuthException.invalid_account()

            user_payload = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "id": str(user.id),
                "customer_status": user.customer_status,
                "email": user.email,
                "is_verified": user.is_verified
            }

            access_token = create_access_token(user_data=user_payload, role="customer")

            refresh_token = create_access_token(user_data=user_payload, role="customer", refresh=True,
                                                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY))

            await user_repository.update_user(condition, {"updated_at": datetime.now()}, session)

            await login_security_service.handle_successful_login(email, request, session)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_payload,
            }

        except Exception as e:
            logger.error(f"Đăng nhập thất bại cho {email}: {str(e)}")
            AuthException.login_failed()











