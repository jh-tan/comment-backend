from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import repositories, schemas
from app.api import deps
from app.models.user import User
from app.utils.permissions import ensure_comment_permission

router = APIRouter()


@router.get("/comment/{comment_id}", response_model=List[schemas.CommentHistory])
async def read_comment_history(
    *,
    db: AsyncSession = Depends(deps.get_db),
    comment_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    comment = await repositories.comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    ensure_comment_permission(current_user, comment, "read")
    
    history = await repositories.comment_history.get_by_comment(
        db, comment_id=comment_id, skip=skip, limit=limit
    )
    return history


@router.get("/{history_id}", response_model=schemas.CommentHistory)
async def read_history_entry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    history_id: int,
    current_user: User = Depends(deps.get_current_user),
):
    history = await repositories.comment_history.get(db, id=history_id)
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    comment = await repositories.comment.get(db, id=history.comment_id)
    ensure_comment_permission(current_user, comment, "read")
    
    return history
