from datetime import datetime, timedelta, timezone
import json

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.domains.login_session import LoginSession
from src.schemas.auth import SessionContent


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    # db에서 가져오는 걸로 바꿔야 함 -> 서비스로 옮긴다
    async def find_session(self, session_id: str) -> SessionContent | None:
        result = await self.session.exec(
            select(LoginSession).where(LoginSession.id == session_id)
        )

        result_data = result.first()
        if not result_data:
            return None

        session_content_json = json.loads(result_data.session_data)
        return SessionContent(
            id=session_content_json["id"],
            nickname=session_content_json["nickname"],
            role=session_content_json["role"],
            expire=session_content_json["expire"],
        )

    async def insert_session(
        self, session_id: str, content: SessionContent, expires_delta: timedelta
    ) -> str:
        expire = datetime.now(tz=timezone.utc) + expires_delta
        content.expire = expire

        new_login_session = LoginSession(
            id=session_id, session_data=content.model_dump_json()
        )

        self.session.add(new_login_session)
        await self.session.commit()

        return session_id

    async def delete_session(self, login_session: LoginSession):
        await self.session.delete(login_session)
        await self.session.commit()
