import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.apis.comment import router as comment_router
from src.apis.common import router as common_router
from src.apis.image import router as image_router
from src.apis.like import router as like_router
from src.apis.notification import router as notification_router
from src.apis.post import router as post_router
from src.apis.user import router as user_router
from src.database import db_init
from src.middlewares.rate_limit import BucketRateLimitMiddleware
from src.scheduler import scheduler_shutdown


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_init(app):
        async with scheduler_shutdown(app):
            yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=post_router)
app.include_router(router=user_router)
app.include_router(router=comment_router)
app.include_router(router=common_router)
app.include_router(router=like_router)
app.include_router(router=notification_router)
app.include_router(router=image_router)

# 테스트시 처리율 제한 비활성화
if os.environ.get("TESTING") != "True":
    app.add_middleware(BucketRateLimitMiddleware)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
