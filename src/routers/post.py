from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.post import Post
from src.models.post import Post as PostModel
from src.database import Base


router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/")
async def create_post(post: Post, db: AsyncSession = Depends(Base.get_db)):
    new_post = PostModel(author=post.author, title=post.title, content=post.content)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post.id


@router.get("/", response_model=List[Post])
async def get_post_list(db: AsyncSession = Depends(Base.get_db)):
    result = await db.execute(select(PostModel))
    posts = result.scalars()._allrows()
    return posts


@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: int, db: AsyncSession = Depends(Base.get_db)):
    result = await db.execute(
                select(PostModel)
                .where(PostModel.id == post_id)
            )
    post = result.scalars().first()
    return post