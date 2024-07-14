from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CreateCommentRequest(BaseModel):
    content: str


class CreateCommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime


class CommentOneResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime


class CommentsResponse(BaseModel):
    posts: List[CommentOneResponse]


class EditComment(BaseModel):
    content: Optional[str] = None
