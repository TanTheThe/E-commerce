import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from src.database.redis import check_login_rate_limit, check_rate_limit
from src.cache.cache_keys import CacheKeys


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.environment = os.getenv("ENVIRONMENT", "development")

    async def dispatch(self, request: Request, call_next):
        if self.environment == "production":
            if request.url.scheme != "https":
                forwarded_proto = request.headers.get("X-Forwarded-Proto", "")

                if forwarded_proto.lower() != "https":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="HTTPS required"
                    )

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        if self.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

def register_middleware(app: FastAPI):
    app.add_middleware(SecurityMiddleware)

    origins = [
        "http://localhost:5173",
        "http://localhost:8000",  # nếu dùng React
        "http://127.0.0.1:8000",
        "http://localhost:5174",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"]
    )
    
class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    @staticmethod
    async def check_login_limit(request: Request):
        """
        Check rate limit cho login endpoint
        Sử dụng như dependency trong login route
        
        Example:
            @router.post("/login")
            async def login(
                credentials: LoginSchema,
                _: None = Depends(RateLimitMiddleware.check_login_limit)
            ):
                # Login logic
                pass
        """
        client_ip = request.client.host
        
        is_allowed, attempts, retry_after = await check_login_rate_limit(client_ip)
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Too many login attempts. Please try again later.",
                    "retry_after": retry_after,
                    "attempts": attempts
                }
            )
    
    
    @staticmethod
    async def check_api_limit(
        request: Request,
        max_requests: int = 100,
        window: int = 60
    ):
        """
        Generic API rate limit
        
        Example:
            @router.get("/api/resource")
            async def get_resource(
                _: None = Depends(
                    lambda r: RateLimitMiddleware.check_api_limit(r, 50, 60)
                )
            ):
                pass
        """
        client_ip = request.client.host
        key = f"rate_limit:api:{client_ip}:{request.url.path}"
        
        is_allowed, attempts, retry_after = await check_rate_limit(
            key, max_requests, window
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "retry_after": retry_after
                }
            )    


