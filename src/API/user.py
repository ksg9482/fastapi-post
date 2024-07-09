from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.auth import encode_access_token, verify_password
from src.schemas.user import LoginRequest, LoginResponse, SignUpRequest, SignUpResponse
from src.service.user import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SignUpResponse)
async def signup(
    signup_user: SignUpRequest, service: UserService = Depends(UserService)
) -> SignUpResponse:
    new_user = await service.signup_account(
        name=signup_user.name, password=signup_user.password
    )

    return new_user


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    login_user: LoginRequest,
    service: UserService = Depends(UserService),
) -> LoginResponse:
    user = await service.find_user_by_name(login_user.name)

    if not user:
        raise HTTPException(status_code=400, detail="User not exists")

    if not verify_password(user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    token_value = {
        "id": user.id,
        "name": user.name,
    }
    access_token = encode_access_token(token_value, timedelta(hours=1))
    response.set_cookie(
        key="access_token", value=access_token.get("access_token"), httponly=True
    )

    return access_token
