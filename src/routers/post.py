from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base
from src.models.post import Post as PostModel
from src.schemas.post import Post

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, db: AsyncSession = Depends(Base.get_db)) -> int:
    new_post = PostModel(author=post.author, title=post.title, content=post.content)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post.id


@router.get("/", response_model=List[Post], status_code=status.HTTP_200_OK)
async def get_post_list(db: AsyncSession = Depends(Base.get_db)) -> List[Post]:
    result = await db.execute(select(PostModel))
    posts = result.scalars().all()
    return posts


@router.get("/{post_id}", response_model=Post, status_code=status.HTTP_200_OK)
async def get_post(post_id: int, db: AsyncSession = Depends(Base.get_db)) -> Post:
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalars().first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found"
        )

    return post
