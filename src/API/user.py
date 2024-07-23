from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from src.auth import (
    delete_session,
    find_session,
    generate_session_id,
    insert_session,
    verify_password,
)
from src.schemas.user import LoginRequest, LoginResponse, SignUpRequest, SignUpResponse
from src.service.user import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SignUpResponse)
async def signup(
    signup_user: SignUpRequest, service: UserService = Depends(UserService)
) -> SignUpResponse:
    new_user = await service.signup_account(
        nickname=signup_user.nickname, password=signup_user.password
    )

    return new_user


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    login_user: LoginRequest,
    service: UserService = Depends(UserService),
    session_id: Optional[str] = Cookie(None),
) -> LoginResponse:
    user = await service.find_user_by_name(login_user.nickname)

    if not user:
        raise HTTPException(status_code=400, detail="User not exists")

    if not verify_password(user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    session_value = {
        "id": user.id,
        "nickname": user.nickname,
    }
    session = find_session(session_id)
    new_session_id = session_id if session else generate_session_id()

    insert_session(
        session_id=new_session_id,
        content=session_value,
        expires_delta=timedelta(days=1),
    )

    response.set_cookie(key="session_id", value=new_session_id, httponly=True)

    return {"session_id": new_session_id}


async def logout(session_id: Optional[str] = Cookie(None)) -> None:
    delete_session(session_id)
    return
