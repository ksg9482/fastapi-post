from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth import get_current_user
from src.schemas.post import (
    EditPost,
    CreatePostRequest,
    CreatePostResponse,
    PostsResponse,
    PostOneResponse,
    EditPostWhole,
)
from src.servicies.post import PostService
from src.domains.user import Role

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=CreatePostResponse
)
async def create_post(
    post: CreatePostRequest,
    service: PostService = Depends(PostService),
    current_user=Depends(get_current_user),
) -> int:
    # Request에 넣는 방식 잘 안씀 -> 블랙박스라 모르게됨. 주입으로 넣는 방식 채택
    user_id = current_user["id"]

    new_post = await service.create_post(
        user_id=user_id, title=post.title, content=post.content
    )

    return new_post


@router.get("/", response_model=PostsResponse, status_code=status.HTTP_200_OK)
async def get_post_list(
    page: Optional[int] = Query(1), service: PostService = Depends(PostService)
) -> PostsResponse:
    posts = await service.post_list(page)
    posts_response = {"posts": posts}
    return posts_response


@router.get(
    "/{post_id}", response_model=PostOneResponse, status_code=status.HTTP_200_OK
)
async def get_post(
    post_id: int, service: PostService = Depends(PostService)
) -> PostOneResponse:
    post = await service.post_find_one(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    post.author = post.user.nickname
    post.content = post.post_content.content
    return post


@router.patch("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_post(
    post_id: int,
    edit_post: EditPost,
    service: PostService = Depends(PostService),
    current_user=Depends(get_current_user),
) -> None:
    user_id = current_user["id"]
    user_role = current_user["role"]

    post = await service.post_find_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    if (not post.author_id == user_id) and (not user_role == Role.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 수정할 수 있습니다",
        )

    await service.edit_post(post=post, title=edit_post.title, content=edit_post.content)

    return


@router.put("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_post_whole(
    post_id: int,
    edit_post: EditPostWhole,
    service: PostService = Depends(PostService),
    current_user=Depends(get_current_user),
) -> None:
    user_id = current_user["id"]
    user_role = current_user["role"]

    post = await service.post_find_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    if (not post.author_id == user_id) and (not user_role == Role.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 수정할 수 있습니다",
        )

    await service.edit_post(post=post, title=edit_post.title, content=edit_post.content)

    return


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    service: PostService = Depends(PostService),
    current_user=Depends(get_current_user),
) -> None:
    user_id = current_user["id"]
    user_role = current_user["role"]

    post = await service.post_find_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    if (not post.author_id == user_id) and (not user_role == Role.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 삭제할 수 있습니다",
        )

    await service.delete_post(post)

    return
