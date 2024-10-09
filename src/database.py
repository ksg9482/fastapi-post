from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis import Redis
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import config
from src.consistent_hash import ConsistentHash

DATABASE_URL = config.DATABASE_URL
REDIS_URL = config.REDIS_URL
engine = AsyncEngine(create_engine(url=DATABASE_URL, pool_size=20, max_overflow=0))
redis = aioredis.from_url(url=REDIS_URL, encoding="utf-8", decode_responses=True)


@asynccontextmanager
async def db_init(app: FastAPI):
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


async def get_session() -> AsyncSession:  # type: ignore
    AsyncSessionLocal = sessionmaker(  # type: ignore
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine,
        class_=AsyncSession,
    )
    async with AsyncSessionLocal() as session:
        yield session


class RedisConnectionPool:
    def __init__(self, servers):
        self.connections = {}
        for server in servers:
            self.connections[server] = aioredis.from_url(f"redis://{server}")

    async def get_connection(self, server):
        return await self.connections[server]


# 캐시 서버 목록
cache_servers = ["localhost:6379", "localhost:6380", "localhost:6381"]

# 애플리케이션 시작 시 초기화
redis_pool = RedisConnectionPool(cache_servers)
consistent_hash = ConsistentHash(cache_servers)


async def get_redis(key: str | None = None) -> Redis:
    if not key:
        key = ""
    server, _ = consistent_hash.get_node(key)
    return await redis_pool.get_connection(server)  # type: ignore
