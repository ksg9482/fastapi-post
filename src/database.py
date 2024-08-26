from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from config import config

# TODO import 문 포매팅이 안되어 있는듯. pre-commit run

DATABASE_URL = config.DATABASE_URL
engine = AsyncEngine(create_engine(url=DATABASE_URL, pool_size=20, max_overflow=0))


@asynccontextmanager
async def db_init(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


async def get_session() -> AsyncSession:
    AsyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
    )
    async with AsyncSessionLocal() as session:
        yield session
