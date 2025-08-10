import strawberry
from typing import Optional
from datetime import datetime


@strawberry.type
class UserType:
    id: int
    username: str
    group: str


@strawberry.type
class CommentType:
    id: int
    content: str
    user_id: int = strawberry.field(name="userId")
    created_at: datetime = strawberry.field(name="createdAt") 
    updated_at: Optional[datetime] = strawberry.field(name="updatedAt")
    user: Optional[UserType] = None


@strawberry.type
class CommentHistoryType:
    id: int
    comment_id: int
    timestamp: datetime
    old_value: Optional[str]
    new_value: str


@strawberry.input
class UserInput:
    username: str
    password: str
    group: str


@strawberry.input
class CommentInput:
    content: str


@strawberry.input
class CommentUpdateInput:
    content: Optional[str] = None