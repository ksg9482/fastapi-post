from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CreatePostRequest(BaseModel):
    title: str
    content: str


class CreatePostResponse(BaseModel):
    id: int
    author: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class PostOneResponse(BaseModel):
    id: int
    author: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class PostsResponse(BaseModel):
    posts: List[PostOneResponse]


class EditPost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class EditPostWhole(BaseModel):
    title: str
    content: str
