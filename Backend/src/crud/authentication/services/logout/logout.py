from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Request
from src.crud.authentication.services.logout.token_blacklist_service import TokenBlacklistService
from src.errors.authentication import AuthException
from src.schemas.user import UserRole
import logging

token_blacklist_service = TokenBlacklistService()

logger = logging.getLogger(__name__)

class LogoutService:
    async def revoke_token(self, token_details: dict, request: Request, session: AsyncSession, role: UserRole):
        token_details = await self.validate_token_details(token_details)

        jti = token_details['jti']
        user_data = token_details['user']
        user_id = user_data['id']
        exp = token_details['exp']

        if not jti:
            AuthException.token_invalid()

        is_blacklisted = await token_blacklist_service.jwt_in_blocklist(jti)

        if is_blacklisted:
            logger.warning(f"Token đã nằm trong blacklist: jti={jti}")
            return True

        ttl = int(exp - datetime.now().timestamp())

        if ttl <= 0:
            logger.warning(f"Token đã hết hạn: jti={jti}")
            return True

        ttl += 60

        meta_data = {
            "user_id": user_id,
            "role": role.value,
            "logout_at": datetime.now().isoformat()
        }

        success = await token_blacklist_service.add_jwt_to_blocklist(
            jti, ttl, meta_data
        )

        if not success:
            AuthException.cant_logout()

        return True

    async def validate_token_details(self, token_details: dict):
        required_fields = ['jti', 'user', 'exp']

        for field in required_fields:
            if field not in token_details:
                AuthException.token_invalid()

        user_data = token_details.get('user', {})
        if not user_data.get('id'):
            AuthException.token_invalid()

        return token_details