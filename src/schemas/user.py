from pydantic import BaseModel


class SignUpRequest(BaseModel):
    name: str
    password: str


class SignUpResponse(BaseModel):
    id: int
    name: str


class LoginRequest(BaseModel):
    name: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
