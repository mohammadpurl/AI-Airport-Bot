from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
import os
from app.config import Settings, get_settings
import asyncpg

# import asyncpg
# import asyncio

settings = get_settings()

# PostgreSQL connection
# engine = create_async_engine(
#     f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
#     echo=True,
# )

# SQLite connection
engine = create_async_engine(
    "sqlite+aiosqlite:///./sql_app.db",
    echo=True,
)

# ساخت session factory
async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# ─────────────────────────────
# 🎯 Base کلاس مدل‌ها
# ─────────────────────────────
Base = declarative_base()


# ─────────────────────────────
# ⛓️ Dependency برای FastAPI
# ─────────────────────────────
@asynccontextmanager
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create database if it doesn't exist"""
    try:
        # PostgreSQL database creation
        # Connect to postgres server
        # sys_conn = await asyncpg.connect(
        #     host=settings.POSTGRES_HOST,
        #     port=settings.POSTGRES_PORT,
        #     user=settings.POSTGRES_USER,
        #     password=settings.POSTGRES_PASSWORD,
        #     database="postgres",  # Connect to default postgres database
        # )

        # # Check if database exists
        # exists = await sys_conn.fetchval(
        #     "SELECT 1 FROM pg_database WHERE datname = $1", settings.POSTGRES_DB
        # )

        # if not exists:
        #     # Create database
        #     await sys_conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
        #     print(f"Database {settings.POSTGRES_DB} created successfully")

        # await sys_conn.close()

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e


# Create tables
async def create_tables():
    from app.models.user import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
