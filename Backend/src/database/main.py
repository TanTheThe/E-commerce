from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from src.config import Config
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import event
import time

engine: AsyncEngine = create_async_engine(
    url=Config.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    future=True,
    echo=False
)

def setup_query_logger(engine):
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()
        print(f"\n[SQL START] {statement}")

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - context._query_start_time
        print(f"[SQL END] Took: {total:.4f} seconds")

setup_query_logger(engine)

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



