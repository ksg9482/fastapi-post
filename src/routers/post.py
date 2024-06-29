from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base
from src.models.post import Post as PostModel
from src.models.user import User as UserModel
from src.schemas.post import EditPost, Post
from src.middlewares import jwt_middleware

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
@jwt_middleware
async def create_post(
    request: Request, post: Post, db: AsyncSession = Depends(Base.get_db)
) -> int:
    """
    return created post id
    """
    user_id = request.state.user["id"]

    new_post = PostModel(
        user_id=user_id, author=post.author, title=post.title, content=post.content
    )
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
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    return post


@router.put("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
@jwt_middleware
async def edit_post(
    request: Request,
    post_id: int,
    edit_post: EditPost,
    db: AsyncSession = Depends(Base.get_db),
) -> None:
    user_id = request.state.user["id"]

    result = await db.execute(
        select(PostModel, UserModel)
        .join(UserModel, PostModel.user_id == UserModel.id)
        .where(PostModel.id == post_id)
    )
    post = result.scalars().first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    if not post.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성자만 수정할 수 있습니다",
        )

    post.title = edit_post.title
    post.content = edit_post.content

    await db.execute(
        update(PostModel)
        .where(PostModel.id == post_id)
        .values(title=edit_post.title, content=edit_post.content)
    )
    await db.commit()

    return


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
@jwt_middleware
async def delete_post(
    request: Request, post_id: int, db: AsyncSession = Depends(Base.get_db)
) -> None:
    user_id = request.state.user["id"]

    result = await db.execute(
        select(PostModel)
        .join(UserModel, PostModel.user_id == UserModel.id)
        .where(PostModel.id == post_id)
    )
    post = result.scalars().first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    if not post.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성자만 삭제할 수 있습니다",
        )

    await db.execute(delete(PostModel).where(PostModel.id == post_id))
    await db.commit()

    return
