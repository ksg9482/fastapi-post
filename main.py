from fastapi import FastAPI
import uvicorn

from src.routers.post import router as post_router
from src.database import Base, engine

async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    lifespan=app_lifespan
)

app.include_router(post_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)