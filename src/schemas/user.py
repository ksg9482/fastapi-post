import re
from pydantic import BaseModel, Field, field_validator


class SignUpRequest(BaseModel):
    name: str
    password: str = Field(
        min_length=8,
        description="비밀번호는 8자 이상, 대문자 1자리 이상 포함",
    )

    @field_validator("password", mode="after")
    @classmethod
    def check_uppercase(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("문자열에 대문자가 하나 이상 포함되어야 합니다")
        return v


class SignUpResponse(BaseModel):
    id: int
    name: str


class LoginRequest(BaseModel):
    name: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
