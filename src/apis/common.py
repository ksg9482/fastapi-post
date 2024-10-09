from fastapi import APIRouter, status

from src.config import config
from src.database import consistent_hash
from src.schemas.common import EditRateLimitRequest

router = APIRouter(tags=["common"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def health() -> None:
    """
    health check
    """
    return


@router.patch("/update_rate_limit", status_code=status.HTTP_200_OK)
async def update_rate_limit(request: EditRateLimitRequest):
    if request.requests_per_minute:
        config.REQUESTS_PER_MINUTE = request.requests_per_minute
    if request.bucket_size:
        config.BUCKET_SIZE = float(request.bucket_size)

    return {
        "message": f"REQUESTS_PER_MINUTE={config.REQUESTS_PER_MINUTE}, BUCKET_SIZE={config.BUCKET_SIZE}"
    }


@router.post("/set_virtual_nodes")
async def set_virtual_nodes(virtual_nodes: int):
    consistent_hash.set_virtual_nodes(virtual_nodes)
    return {"message": f"Virtual nodes set to {virtual_nodes}"}
