from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.comment_history import CommentHistory
from app.schemas.comment_history import CommentHistoryCreate, CommentHistoryCreate

class CommentHistoryRepository(BaseRepository[CommentHistory, CommentHistoryCreate, CommentHistoryCreate]):
    
    async def get_by_comment(
        self, db: AsyncSession, *, comment_id: int, skip: int = 0, limit: int = 100
    ) -> List[CommentHistory]:
        stmt = (
            select(CommentHistory)
            .where(CommentHistory.comment_id == comment_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_history_entry(
        self,
        db: AsyncSession,
        *,
        comment_id: int,
        old_value: str = None,
        new_value: str
    ) -> CommentHistory:
        db_obj = CommentHistory(
            comment_id=comment_id,
            old_value=old_value,
            new_value=new_value
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


comment_history = CommentHistoryRepository(CommentHistory)