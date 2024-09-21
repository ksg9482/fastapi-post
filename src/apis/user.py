from datetime import datetime, timedelta

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from ulid import ULID

from src.auth import get_current_user, verify_password
from src.schemas.auth import SessionContent
from src.schemas.user import (
    LoginRequest,
    LoginResponse,
    NotificationsResponse,
    NotificationsResponseBody,
    SignUpRequest,
    SignUpResponse,
    UploadProfileImgResponse,
    UserResponse,
)
from src.servicies.auth import AuthService
from src.servicies.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SignUpResponse)
async def signup(
    request: SignUpRequest,
    service: UserService = Depends(UserService),
) -> SignUpResponse:
    user = await service.get_user_by_nickname(request.nickname)

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 가입한 유저입니다"
        )

    new_user = await service.signup_account(
        nickname=request.nickname, password=request.password
    )

    if not new_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="유저 생성에 실패했습니다.",
        )

    return SignUpResponse(id=new_user.id, nickname=new_user.nickname)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    request: LoginRequest,
    user_service: UserService = Depends(UserService),
    auth_service: AuthService = Depends(AuthService),
    session_id: str | None = Cookie(None),
) -> LoginResponse:
    user = await user_service.get_user_by_nickname(request.nickname)

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

    session = await auth_service.find_session(session_id)
    new_session_id = (
        session_id
        if (session and session_id)
        else str(ULID.from_datetime(datetime.now()))
    )
    session_value = SessionContent(id=user.id, nickname=user.nickname, role=user.role)  # type: ignore
    await auth_service.insert_session(
        session_id=new_session_id,
        content=session_value,
        expires_delta=timedelta(days=1),
    )
    response.set_cookie(key="session_id", value=new_session_id, httponly=True)

    return LoginResponse(session_id=new_session_id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    session_id: str | None = Cookie(None),
    auth_service: AuthService = Depends(AuthService),
) -> None:
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="세션 아이디가 없습니다."
        )

    session = await auth_service.find_session(session_id)

    if session:
        await auth_service.delete_session(session)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 세션입니다"
        )


@router.get("/notifications", status_code=status.HTTP_200_OK)
async def user_notifications(
    service: UserService = Depends(UserService),
    current_user: SessionContent = Depends(get_current_user),
) -> NotificationsResponse:
    user_id = current_user.id

    notifications = await service.get_user_notification(user_id=user_id)
    response = NotificationsResponse(
        notifications=[
            NotificationsResponseBody(
                id=notification.id,  # type: ignore
                post_id=notification.post_id,
                user_id=notification.user_id,
            )
            for notification in notifications
        ]
    )

    return response


@router.get("/profile", status_code=status.HTTP_200_OK)
async def user_profile(
    service: UserService = Depends(UserService),
    current_user: SessionContent = Depends(get_current_user),
) -> UserResponse:
    user_id = current_user.id

    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 유저입니다"
        )
    response = UserResponse(
        id=user.id,  # type: ignore
        nickname=user.nickname,
        role=user.role,
        profile_img=user.profile_img_url if user.profile_img_url else "",
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

    return response


@router.post("/profile_img", status_code=status.HTTP_201_CREATED)
async def upload_profile_img(
    file: UploadFile,
    service: UserService = Depends(UserService),
    current_user: SessionContent = Depends(get_current_user),
) -> UploadProfileImgResponse:
    user_id = current_user.id

    allow_extension = ["jpg", "jpeg", "png"]
    if not file.content_type or not file.content_type.startswith("image"):
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
    content = await file.read()
    filename = f"{str(ULID.from_datetime(datetime.now()))}.{file_extention}"  # uuid로 유니크한 파일명으로 변경

    img_url = await service.save_profile_img(
        user_id=user_id, img_name=filename, img_content=content
    )

    response = UploadProfileImgResponse(img_url=img_url)
    return response
