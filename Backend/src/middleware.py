import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


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

