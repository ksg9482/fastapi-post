from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from fastapi import Cookie, HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
session_data = {}


# TODO: type hint 추가
def generate_session_id():
    return str(uuid4())


def insert_session(session_id: str, content: dict, expires_delta: timedelta) -> str:
    expire = datetime.now(tz=timezone.utc) + expires_delta
    content.update({"expire": expire})
    session_data[session_id] = content
    return session_id


def find_session(session_id: str) -> dict | None:
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


# TODO: Type hint에 None이 필요가 없을 듯?
def get_current_user(session_id: Optional[str] = Cookie(None)) -> dict | None:
    session_data = find_session(session_id)
    is_expired = datetime.now(tz=timezone.utc) >= session_data["expire"]
    if (session_id is None) or (session_data is None) or is_expired:
        raise HTTPException(
            # TODO: 좀 더 좋은 에러 메시지는 뭘까?
            status_code=status.HTTP_401_UNAUTHORIZED, detail="세션이 유효하지 않습니다"
        )
    return session_data
