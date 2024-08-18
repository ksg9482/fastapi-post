from datetime import datetime
from pydantic import BaseModel, Field

from src.domains.user import Role


class SessionContent(BaseModel):
    id: int
    nickname: str
    role: Role
    expire: datetime | None = Field(default=None)
