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
from src.servicies.user import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SignUpResponse)
async def signup(
    request: SignUpRequest,
    service: UserService = Depends(UserService),
) -> SignUpResponse:
    user = await service.find_user_by_name(request.nickname)

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 가입한 유저입니다"
        )

    new_user = await service.signup_account(
        nickname=request.nickname, password=request.password
    )

    return SignUpResponse(id=new_user.id, nickname=new_user.nickname)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    request: LoginRequest,
    service: UserService = Depends(UserService),
    session_id: Optional[str] = Cookie(None),
) -> LoginResponse:
    user = await service.find_user_by_name(request.nickname)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="존재하지 않는 유저입니다"
        )

    if not verify_password(
        plain_password=request.password, hashed_password=user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 비밀번호입니다"
        )

    session_value = {"id": user.id, "nickname": user.nickname, "role": user.role}
    session = find_session(session_id)
    new_session_id = session_id if session else generate_session_id()

    insert_session(
        session_id=new_session_id,
        content=session_value,
        expires_delta=timedelta(days=1),
    )

    response.set_cookie(key="session_id", value=new_session_id, httponly=True)

    return LoginResponse(session_id=new_session_id)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(session_id: Optional[str] = Cookie(None)) -> None:
    delete_session(session_id)
