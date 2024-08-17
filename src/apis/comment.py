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
    # TODO: post_id가 request body에 들어가야 하지 않을까?
    # COMMENT: 다른 대안으로 POST /posts/{post_id}/comments 
    request: CreateCommentRequest,
    # TODO: service -> comment_service
    service: CommentService = Depends(CommentService),
    post_service: PostService = Depends(PostService),
    current_user=Depends(get_current_user),  # TODO: type hint -> mypy 적용해보기 (+ pre-commit-config 추가히기)
) -> CreateCommentResponse:
    # COMMENT: 본인만의 개행 기준이 있는지? 있으면 좋을듯.
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


# TODO: GET /comments?user_id={user_id}
# TODO: GET /comments?post_id={post_id}
# TODO: GET /comments?user_id={user_id}&post_id={post_id}
# TODO: 아래 두 엔드포인트 위처럼 합치기 + user_id 여러 개 받기 
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

    # TODO: 예측 가능하고 일관되게 메서드명 지어보기
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
