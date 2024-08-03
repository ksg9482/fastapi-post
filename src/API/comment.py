from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth import get_current_user
from src.schemas.post import (
    PostsResponse,
)
from src.schemas.comment import (
    CreateCommentRequest,
    CreateCommentResponse,
    CommentsResponse,
    EditComment,
)
from src.service.comment import CommentService
from src.service.post import PostService
from src.domain.user import Role

router = APIRouter(prefix="/comments", tags=["comments"])


# post_id로 바로 부르는건 햇갈릴거 같다. commets/1이 1번 코멘트가 아니라 post1에 코멘트 다는 거라고 직관적으로 모름
# POST /comments?post_id=1 이게 나을듯
# POST /comments/list?post_id=1
@router.post(
    "/{post_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateCommentResponse,
)
async def create_comment(
    post_id: int,
    comment: CreateCommentRequest,
    service: CommentService = Depends(CommentService),
    post_service: PostService = Depends(PostService),
    current_user=Depends(get_current_user),
) -> int:
    user_id = current_user["id"]

    post = await post_service.post_find_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    new_comment = await service.create_comment(
        user_id=user_id, post_id=post_id, content=comment.content
    )

    return new_comment


@router.get(
    "/by_post/{post_id}",
    response_model=CommentsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_comment_list_by_post(
    post_id: int,
    page: Optional[int] = Query(1),
    service: CommentService = Depends(CommentService),
) -> PostsResponse:
    comments = await service.comment_list_by_post(page, post_id)
    comments_response = {"comments": comments}

    return comments_response


@router.get(
    "/by_user/{user_id}",
    response_model=CommentsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_comment_list_by_user(
    user_id: int,
    page: Optional[int] = Query(1),
    service: CommentService = Depends(CommentService),
) -> PostsResponse:
    comments = await service.comment_list_by_user(page, user_id)
    comments_response = {"comments": comments}

    return comments_response


@router.patch("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_comment(
    comment_id: int,
    edit_comment: EditComment,
    service: CommentService = Depends(CommentService),
    current_user=Depends(get_current_user),
) -> None:
    user_id = current_user["id"]
    user_role = current_user["role"]

    comment = await service.comment_one(comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 코멘트입니다"
        )

    if (not comment.author_id == user_id) and (not user_role == Role.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 수정할 수 있습니다",
        )

    await service.edit_comment(comment=comment, content=edit_comment.content)

    return


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    service: CommentService = Depends(CommentService),
    current_user=Depends(get_current_user),
) -> None:
    user_id = current_user["id"]
    user_role = current_user["role"]

    comment = await service.comment_one(comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 코멘트입니다"
        )

    if (not comment.author_id == user_id) and (not user_role == Role.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 삭제할 수 있습니다",
        )

    await service.delete_comment(comment)

    return
