from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from src.config import Config
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
import time

engine: AsyncEngine = create_async_engine(
    url=Config.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    future=True
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session(request: Request) -> AsyncSession:
    # start = time.time()
    # SessionLocal = request.app.state.session
    # session = SessionLocal()
    # print("Create session took", time.time() - start)
    # try:
    #     yield session
    # finally:
    #     await session.close()

    SessionLocal = request.app.state.session
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()



