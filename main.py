import uvicorn
from fastapi import FastAPI

from src.database import Base, engine
from src.routers.post import router as post_router
from src.routers.user import router as user_router


async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=app_lifespan)

app.include_router(router=post_router)
app.include_router(router=user_router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8080, reload=True)
