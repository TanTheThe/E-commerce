from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.authentication.services.token_blacklist_service import TokenBlacklistService
from src.crud.authentication.utils import decode_url_safe_token
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from fastapi import Request
from src.schemas.user import UserRole
import logging

token_blacklist_service = TokenBlacklistService()
user_repository = UserRepository()

logger = logging.getLogger(__name__)

class VerifyUserAccountService:
    async def verify_user_account(self, token: str, role: UserRole, request: Request, session: AsyncSession):
        token_data = decode_url_safe_token(
            token,
            role=role.value,
            purpose="create_account"
        )

        if token_data is None:
            AuthException.authentication_error()

        user_email = token_data.get('email')
        user_id = token_data.get('user_id')

        if not user_email and not user_id:
            AuthException.authentication_error()

        is_blacklisted = await token_blacklist_service.token_in_blocklist(
            token=token,
            role=role.value,
            purpose="create_account",
            request=request
        )

        if is_blacklisted:
            AuthException.token_already_used()

        condition = [
            User.email == user_email,
            User.id == user_id,
            User.deleted_at.is_(None),
        ]

        user = await user_repository.get_user(session=session, where_conditions=condition)
        if user is None:
            AuthException.user_not_found()

        if user.is_verified:
            await token_blacklist_service.add_token_to_blocklist(
                token=token,
                role=role.value,
                purpose="create_account",
                request=request,
                metadata={"reason": "already_verified"}
            )

        if role == UserRole.CUSTOMER and not user.is_customer:
            AuthException.authentication_error()
        if role == UserRole.STAFF and not user.is_staff:
            AuthException.authentication_error()

        try:
            update_data = {
                "is_verified": True,
                "updated_at": datetime.now()
            }

            condition_update = [
                User.id == user.id,
                User.deleted_at.is_(None),
            ]

            user_tuple = await user_repository.update_user(condition_update, update_data, session)
            user = user_tuple[0]

            await token_blacklist_service.add_token_to_blocklist(
                token=token,
                role=role.value,
                purpose="create_account",
                request=request,
                metadata={
                    "user_id": str(user.id),
                    "verified_at": datetime.now().isoformat()
                }
            )

            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.error(e)
            AuthException.verification_failed()






