from fastapi.security import HTTPBearer
from fastapi import Request, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from starlette import status
from fastapi.exceptions import HTTPException
from src.cache import redis_manager
from src.crud.authentication.utils import decode_token
from src.database.redis import token_in_blocklist
from redis import asyncio as aioredis
from src.cache.redis_manager import RedisManager
from src.cache.cache_service import CacheService
from src.database.redis import check_login_rate_limit, check_rate_limit
from src.cache.cache_keys import CacheKeys


redis_manager = RedisManager()
cache_service = CacheService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )

        in_blocklist = await token_in_blocklist(token_data['jti'], request)

        if in_blocklist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get new token"
                }
            )

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )


def verify_token_and_get_role(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header bị thiếu hoặc không hợp lệ"
        )

    token = auth_header.split(" ")[1]
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token hết hạn hoặc không hợp lệ"
        )

    role = payload.get("role")
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vai trò không tìm thấy trong token"
        )

    return role


async def admin_role_middleware(role: str = Depends(verify_token_and_get_role)):
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ có admin mới có thể sử dụng tính năng này")


async def customer_role_middleware(role: str = Depends(verify_token_and_get_role)):
    if role != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ có customer mới có thể sử dụng tính năng này")


async def staff_role_middleware(role: str = Depends(verify_token_and_get_role)):
    if role != "staff":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ có staff mới có thể sử dụng tính năng này")
    
    
async def get_redis() -> aioredis.Redis:
    """
    Dependency để lấy Redis client
    Sử dụng trong FastAPI endpoints
    
    Example:
        @app.get("/example")
        async def example(redis: aioredis.Redis = Depends(get_redis)):
            await redis.set("key", "value")
    """
    return redis_manager.redis


async def get_cache_service():
    """
    Dependency để lấy Cache Service
    Sử dụng high-level cache operations
    
    Example:
        @app.get("/products/{id}")
        async def get_product(
            id: str,
            cache: CacheService = Depends(get_cache_service)
        ):
            return await cache.get_or_set(
                f"product:{id}",
                lambda: fetch_product_from_db(id),
                ttl=3600
            )
    """
    return cache_service





