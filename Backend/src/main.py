from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import sessionmaker
from src.database.main import engine, init_db
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from src.api_router import admin_router, customer_router, staff_router
from src.config import Config
from redis.asyncio import Redis
from src.middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = engine
    app.state.session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    app.state.redis = Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=0,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5
    )

    yield

    await app.state.engine.dispose()
    await app.state.redis.aclose()

app = FastAPI(title="E-commerce", version="v1", lifespan=lifespan)

register_middleware(app)

app.include_router(staff_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(customer_router, prefix="/api/v1")
app.mount("/static", StaticFiles(directory="src/static"), name="static")
