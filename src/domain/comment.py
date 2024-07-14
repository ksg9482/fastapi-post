from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, func
from src.domain.user import User
from src.domain.post import Post


class Comment(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    content: str
    created_at: datetime = Field(default=func.now())
    updated_at: datetime = Field(default_factory=func.now)

    author_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="comments")

    post_id: int = Field(foreign_key="post.id")
    post: Post = Relationship(back_populates="comments")
