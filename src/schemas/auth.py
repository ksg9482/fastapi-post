from pydantic import BaseModel


class SessionData(BaseModel):
    id: int
    nickname: str
