from pydantic import BaseModel


class UploadProfileImgResponse(BaseModel):
    id: int
    img_url: str
