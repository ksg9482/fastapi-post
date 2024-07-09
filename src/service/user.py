from fastapi import Depends

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth import hash_password
from src.database import get_session
from src.domain.user import User


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def signup_account(self, name: str, password: str) -> User:
        hashed_password = hash_password(plain_password=password)
        new_user = User(name=name, password=hashed_password)

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def find_user_by_name(self, name: str) -> User | None:
        result = await self.session.exec(select(User).where(User.name == name))
        user = result.first()

        return user
