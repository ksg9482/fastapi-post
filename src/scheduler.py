from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI

from src.servicies.image import ImageService


async def scheduled_image_cleanup(image_service=Depends(ImageService)):
    image_service = ImageService()
    await image_service.remove_old_pending_images()


# 스케줄러 설정
scheduler = AsyncIOScheduler()
scheduler.add_job(scheduled_image_cleanup, "interval", hours=24)
scheduler.start()


# 앱종료시 스케줄링 제거
@asynccontextmanager
async def scheduler_shutdown(app: FastAPI):
    yield
    scheduler.shutdown()
