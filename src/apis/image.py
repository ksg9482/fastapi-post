from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from ulid import ULID

from src.domains.image import SaveType
from src.schemas.image import UploadProfileImgResponse
from src.servicies.image import ImageService

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/profile", status_code=status.HTTP_201_CREATED)
async def upload_profile_img(
    file: UploadFile,
    service: ImageService = Depends(ImageService),
    save_type: SaveType = Query(SaveType.GCP),
    user_id: int | None = Query(None),
) -> UploadProfileImgResponse:

    allow_extension = ["jpg", "jpeg", "png"]
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="요청에 content_type 속성이 없습니다.",
        )
    if not file.content_type.startswith("image"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일만 업로드 가능합니다.",
        )
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일 이름이 없습니다.",
        )
    file_extention = file.filename.split(".")[-1].lower()
    if file_extention not in allow_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드 할 수 없는 이미지 확장자입니다. jpg, jpeg, png 확장자를 이용해 주세요",
        )
    filename = f"{str(ULID.from_datetime(datetime.now()))}.{file_extention}"  # ulid로 유니크한 파일명으로 변경
    new_image = await service.save_profile_img(
        user_id=user_id, img_name=filename, img_content=file, save_type=save_type
    )
    response = UploadProfileImgResponse(
        id=new_image.id, img_url=new_image.name  # type: ignore
    )

    return response
