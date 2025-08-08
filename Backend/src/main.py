from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from src.database.main import engine
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from src.api_router import admin_router, customer_router, public_router
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
        decode_responses=True
    )

    yield

    await app.state.engine.dispose()
    await app.state.redis.close()
    await app.state.redis.connection_pool.disconnect()

app = FastAPI(title="E-commerce", version="v1", lifespan=lifespan)

register_middleware(app)

app.include_router(public_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(customer_router, prefix="/api/v1")
