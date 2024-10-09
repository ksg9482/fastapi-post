from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth import hash_password
from src.database import get_session
from src.domains.image import Image, State, UseType
from src.domains.user import User


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def signup_account(
        self, nickname: str, password: str, img_id: int | None = None
    ) -> User:
        hashed_password = hash_password(plain_password=password)
        new_user = User(nickname=nickname, password=hashed_password)

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        # image ACTIVE 처리
        if img_id:
            await self.session.exec(  # type: ignore
                update(Image)
                .where(Image.id == img_id)  # type: ignore
                .values(state=State.ACTIVE, user_id=new_user.id)
            )
            await self.session.commit()

        return new_user

    async def get_user_by_nickname(self, nickname: str) -> User | None:
        result = await self.session.exec(select(User).where(User.nickname == nickname))
        user = result.first()

        return user

    async def get_user(self, user_id: int) -> User | None:
        result = await self.session.exec(
            select(User)
            .options(
                selectinload(
                    User.images.and_(  # type: ignore
                        Image.state == State.ACTIVE,
                        Image.use_type == UseType.USER_PROFILE,
                    )
                )
            )
            .where(User.id == user_id)
        )
        user = result.first()
        return user
