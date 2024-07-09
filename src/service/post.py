from typing import List, Optional

from fastapi import Depends

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.domain.post import Post


class PostService:
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def create_post(
        self, user_id: int, author: str, title: str, content: str
    ) -> Post:
        new_post = Post(user_id=user_id, author=author, title=title, content=content)
        self.session.add(new_post)
        await self.session.commit()
        await self.session.refresh(new_post)
        return new_post

    async def post_list(self) -> List[Post]:
        result = await self.session.exec(select(Post))
        posts = result.all()
        return list(posts)

    async def post_one(self, post_id: int) -> Post | None:
        result = await self.session.exec(select(Post).where(Post.id == post_id))
        post = result.first()
        return post

    async def edit_post(
        self, post: Post, title: Optional[str] = None, content: Optional[str] = None
    ) -> None:
        if title:
            post.title = title
        if content:
            post.content = content

        self.session.add(post)
        await self.session.commit()

    async def delete_post(self, post: Post):
        await self.session.delete(post)
        await self.session.commit()
