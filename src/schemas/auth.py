from pydantic import BaseModel


class AccessTokenValue(BaseModel):
    id: int
    name: str
