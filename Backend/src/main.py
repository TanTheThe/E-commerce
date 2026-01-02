from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import sessionmaker
from src.cache import redis_manager
from src.database.main import engine, init_db
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from src.api_router import admin_router, customer_router, staff_router
from src.config import Config
from redis.asyncio import Redis
from src.middleware import register_middleware
import logging

from src.cache.redis_manager import RedisManager
from src.database.main import init_db 

logger = logging.getLogger(__name__)

redis_manager = RedisManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.engine = engine
        app.state.session = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        await redis_manager.connect()
        app.state.redis = redis_manager.redis
        logger.info("Redis connected and initialized")
            
        await redis_manager.redis.ping()
        logger.info("Redis ping successful")

        health = await redis_manager.health_check()
        logger.info(f"Redis Status: {health}")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.exception(e)
        raise

    yield
    
    try:
        await redis_manager.disconnect()
        logger.info("Redis disconnected")
        
        await app.state.engine.dispose()
        logger.info("Database connections closed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        logger.exception(e)
    
    logger.info("Application stopped successfully")

app = FastAPI(title="E-commerce", version="v1", lifespan=lifespan)

register_middleware(app)

app.include_router(staff_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(customer_router, prefix="/api/v1")
app.mount("/static", StaticFiles(directory="src/static"), name="static")
