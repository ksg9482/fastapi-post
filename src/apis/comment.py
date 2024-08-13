from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth import get_current_user
from src.schemas.comment import (
    CreateCommentRequest,
    CreateCommentResponse,
    CommentsResponse,
    EditComment,
)
from src.servicies.comment import CommentService
from src.servicies.post import PostService
from src.domains.user import Role

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
    request: CreateCommentRequest,
    service: CommentService = Depends(CommentService),
    post_service: PostService = Depends(PostService),
    current_user=Depends(get_current_user),
) -> CreateCommentResponse:
    user_id = current_user["id"]

    post = await post_service.post_find_one(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 포스트입니다"
        )

    new_comment = await service.create_comment(
        user_id=user_id, post_id=post_id, content=request.content
    )

    return CreateCommentResponse(
        id=new_comment.id,
        author_id=new_comment.author_id,
        post_id=new_comment.post_id,
        content=new_comment.content,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at,
    )


@router.get(
    "/by_post/{post_id}",
    response_model=CommentsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_comment_list_by_post(
    post_id: int,
    page: Optional[int] = Query(1),
    service: CommentService = Depends(CommentService),
) -> CommentsResponse:
    comments = await service.comment_list_by_post(page, post_id)

    return CommentsResponse(
        comments=list([comment.model_dump() for comment in comments])
    )


@router.get(
    "/by_user/{user_id}",
    response_model=CommentsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_comment_list_by_user(
    user_id: int,
    page: Optional[int] = Query(1),
    service: CommentService = Depends(CommentService),
) -> CommentsResponse:
    comments = await service.comment_list_by_user(page, user_id)

    return CommentsResponse(
        comments=list([comment.model_dump() for comment in comments])
    )


@router.patch("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_comment(
    comment_id: int,
    request: EditComment,
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
            detail="작성자 또는 관리자만 수정할 수 있습니다",
        )

    await service.edit_comment(comment=comment, content=request.content)


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
            detail="작성자 또는 관리자만 삭제할 수 있습니다",
        )

    await service.delete_comment(comment)
