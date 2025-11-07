from fastapi import Request

from src.crud.authentication.services.token_blacklist_service import TokenBlacklistService

JTI_EXPIRY = 3600

token_blacklist_service = TokenBlacklistService()

async def add_jti_to_blocklist(jti: str, request: Request) -> None:
    await token_blacklist_service.add_jwt_to_blocklist(jti, request)

async def token_in_blocklist(jti: str, request: Request) -> bool:
    return await token_blacklist_service.jwt_in_blocklist(jti, request)

