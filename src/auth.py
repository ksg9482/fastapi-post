from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Cookie, HTTPException, status
from passlib.context import CryptContext

from src.schemas.auth import SessionContent

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
session_data: dict[str, SessionContent] = {}


def generate_session_id() -> str:
    return str(uuid4())  # uuld로


def insert_session(
    session_id: str, content: SessionContent, expires_delta: timedelta
) -> str:
    expire = datetime.now(tz=timezone.utc) + expires_delta
    content.expire = expire
    session_data[session_id] = content

    return session_id


def find_session(session_id: str) -> SessionContent | None:
    return session_data.get(session_id)


def delete_session(session_id: str) -> None:
    session = find_session(session_id)
    if session:
        session_data.pop(session_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 세션입니다"
        )


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(secret=plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(secret=plain_password, hash=hashed_password)


def get_current_user(session_id: str | None = Cookie(None)) -> SessionContent:
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션 아이디가 입력되지 않았습니다. 다시 로그인 해 주세요",
        )

    session_content = find_session(session_id)
    if not session_content:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="존재하지 않는 세션입니다. 다시 로그인 해 주세요",
        )

    is_expired = datetime.now(tz=timezone.utc) >= session_content.expire
    if is_expired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="만료된 세션입니다. 다시 로그인 해주세요",
        )
    return session_content
