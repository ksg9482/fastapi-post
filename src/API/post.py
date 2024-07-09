from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.schemas.post import (
    EditPost,
    CreatePostRequest,
    CreatePostResponse,
    PostsResponse,
    PostOneResponse,
    EditPostWhole,
)
from src.middlewares import jwt_middleware
from src.service.post import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=CreatePostResponse
)
@jwt_middleware
async def create_post(
    request: Request,
    post: CreatePostRequest,
    service: PostService = Depends(PostService),
) -> int:
    # Request에 넣는 방식 잘 안씀 -> 블랙박스라 모르게됨. 주입으로 넣어보기
    user_id = request.state.user["id"]
    author = request.state.user["name"]

    new_post = await service.create_post(
        user_id=user_id, author=author, title=post.title, content=post.content
    )

    return new_post


@router.get("/", response_model=PostsResponse, status_code=status.HTTP_200_OK)
async def get_post_list(service: PostService = Depends(PostService)) -> PostsResponse:
    posts = await service.post_list()
    posts_response = {"posts": posts}
    return posts_response


@router.get(
    "/{post_id}", response_model=PostOneResponse, status_code=status.HTTP_200_OK
)
async def get_post(
    post_id: int, service: PostService = Depends(PostService)
) -> PostOneResponse:
    post = await service.post_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    return post


@router.patch("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
@jwt_middleware
async def edit_post(
    request: Request,
    post_id: int,
    edit_post: EditPost,
    service: PostService = Depends(PostService),
) -> None:
    user_id = request.state.user["id"]

    post = await service.post_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    if not post.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 수정할 수 있습니다",
        )

    await service.edit_post(post=post, title=edit_post.title, content=edit_post.content)

    return


@router.put("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
@jwt_middleware
async def edit_post_whole(
    request: Request,
    post_id: int,
    edit_post: EditPostWhole,
    service: PostService = Depends(PostService),
) -> None:
    user_id = request.state.user["id"]

    post = await service.post_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    if not post.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 수정할 수 있습니다",
        )

    await service.edit_post(post=post, title=edit_post.title, content=edit_post.content)

    return


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
@jwt_middleware
async def delete_post(
    request: Request,
    post_id: int,
    service: PostService = Depends(PostService),
) -> None:
    user_id = request.state.user["id"]

    post = await service.post_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    if not post.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 삭제할 수 있습니다",
        )

    await service.delete_post(post)

    return
