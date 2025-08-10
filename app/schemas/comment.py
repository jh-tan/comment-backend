from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import User


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class Comment(CommentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: User
    
    class Config:
        from_attributes = True