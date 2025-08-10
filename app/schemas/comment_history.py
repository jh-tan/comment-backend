from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentHistoryBase(BaseModel):
    old_value: Optional[str] = None
    new_value: str


class CommentHistoryCreate(CommentHistoryBase):
    comment_id: int


class CommentHistory(CommentHistoryBase):
    id: int
    comment_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True