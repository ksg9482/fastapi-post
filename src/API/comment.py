from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.schemas.post import (
    PostsResponse,
)
from src.schemas.comment import (
    CreateCommentRequest,
    CreateCommentResponse,
    CommentsResponse,
    EditComment,
)
from src.middlewares import jwt_middleware
from src.service.comment import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/{post_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateCommentResponse,
)
@jwt_middleware
async def create_comment(
    request: Request,
    post_id: int,
    comment: CreateCommentRequest,
    service: CommentService = Depends(CommentService),
) -> int:
    user_id = request.state.user["id"]

    new_comment = await service.create_comment(
        user_id=user_id, post_id=post_id, content=comment.content
    )

    return new_comment


@router.get(
    "/{post_id}", response_model=CommentsResponse, status_code=status.HTTP_200_OK
)
async def get_comment_list_by_post(
    post_id: int,
    page: Optional[int] = Query(1),
    service: CommentService = Depends(CommentService),
) -> PostsResponse:
    comments = await service.comment_list_by_post(page, post_id)
    comments_response = {"posts": comments}

    return comments_response


@router.get(
    "/{user_id}", response_model=CommentsResponse, status_code=status.HTTP_200_OK
)
async def get_comment_list_by_user(
    user_id: int,
    page: Optional[int] = Query(1),
    service: CommentService = Depends(CommentService),
) -> PostsResponse:
    comments = await service.comment_list_by_user(page, user_id)
    comments_response = {"posts": comments}

    return comments_response


@router.patch("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
@jwt_middleware
async def edit_comment(
    request: Request,
    comment_id: int,
    edit_comment: EditComment,
    service: CommentService = Depends(CommentService),
) -> None:
    user_id = request.state.user["id"]

    comment = await service.comment_one(comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 코멘트입니다"
        )

    if not comment.author_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 수정할 수 있습니다",
        )

    await service.edit_comment(comment == comment, content=edit_comment.content)

    return


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
@jwt_middleware
async def delete_comment(
    request: Request,
    comment_id: int,
    service: CommentService = Depends(CommentService),
) -> None:
    user_id = request.state.user["id"]

    comment = await service.comment_one(comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 코멘트입니다"
        )

    if not comment.author_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 삭제할 수 있습니다",
        )

    await service.delete_comment(comment)

    return
