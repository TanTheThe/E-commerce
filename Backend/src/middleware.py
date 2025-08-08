from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def register_middleware(app: FastAPI):
    origins = [
        "http://localhost:5173",
        "http://localhost:8000",  # nếu dùng React
        "http://127.0.0.1:8000",  # production
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