from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.repositories.base import BaseRepository
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    async def get(self, db: AsyncSession, id: int) -> Optional[Comment]:
        return await super().get(
            db, id,
            options=[selectinload(Comment.user)]
        )

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: CommentCreate, user_id: int
    ) -> Comment:
        db_obj = Comment(
            **obj_in.model_dump(),
            user_id=user_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user_group(self, db: AsyncSession, *, user_group: str, skip: int = 0, limit: int = 100) -> List[Comment]:
        result = await db.execute(
            select(Comment)
            .join(User)
            .filter(User.group == user_group)
            .options(selectinload(Comment.user))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.user_id == user_id)
            .options(joinedload(Comment.user))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_user_group_with_user(
        self, db: AsyncSession, *, user_group: str, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        query = (
            select(self.model)
            .join(User)
            .where(User.group == user_group)
            .options(selectinload(self.model.user))  
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_user(self, db: AsyncSession, id: int) -> Optional[Comment]:
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.user))
        )
        result = await db.execute(query)
        return result.scalars().first()


comment = CommentRepository(Comment)