from datetime import datetime
from sqlmodel import (
    Field,
    SQLModel,
    Relationship,
    func,
)
from src.domain.user import User


class Content(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    content: str
    created_at: datetime = Field(default=func.now())
    updated_at: datetime = Field(default_factory=func.now)

    post: "Post" = Relationship(back_populates="content")


class Post(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    title: str
    content_id: int = Field(foreign_key="content.id")
    content: Content = Relationship(back_populates="post")
    # default: 정의한 값으로 정적 채우기
    created_at: datetime = Field(default=func.now())
    # default_factory: 정의한 함수를 해당 시점에 호출해서 채우기
    updated_at: datetime = Field(default_factory=func.now)

    author_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="posts")

    comments: list["Comment"] = Relationship(back_populates="post")

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author
