from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import repositories, schemas
from app.api import deps
from app.models.user import User

from app.utils.permissions import ensure_comment_permission

router = APIRouter()


@router.post("/", response_model=schemas.Comment)
async def create_comment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    comment_in: schemas.comment.CommentCreate,
    current_user: User = Depends(deps.get_current_user),
):
    comment = await repositories.comment.create_with_user(
        db=db, obj_in=comment_in, user_id=current_user.id
    )
    await repositories.comment_history.create_history_entry(
        db=db,
        comment_id=comment.id,
        old_value=None,
        new_value=comment.content
    )
    return comment


@router.get("/", response_model=List[schemas.Comment])
async def read_comments(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    comments = await repositories.comment.get_by_user_group(
        db, user_group=current_user.group, skip=skip, limit=limit
    )
    return comments


@router.get("/{comment_id}", response_model=schemas.Comment)
async def read_comment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    comment_id: int,
    current_user: User = Depends(deps.get_current_user),
):
    comment = await repositories.comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    ensure_comment_permission(current_user, comment, "read")
    return comment


@router.put("/{comment_id}", response_model=schemas.Comment)
async def update_comment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    comment_id: int,
    comment_in: schemas.CommentUpdate,
    current_user: User = Depends(deps.get_current_user),
):
    comment = await repositories.comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    ensure_comment_permission(current_user, comment, "update")

    old_content = comment.content
    comment = await repositories.comment.update(db, db_obj=comment, obj_in=comment_in)

    if comment_in.content and comment_in.content != old_content:
        await repositories.comment_history.create_history_entry(
            db=db,
            comment_id=comment.id,
            old_value=old_content,
            new_value=comment.content
        )

    return comment


@router.delete("/{comment_id}", response_model=schemas.Comment)
async def delete_comment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    comment_id: int,
    current_user: User = Depends(deps.get_current_user),
):
    comment = await repositories.comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    ensure_comment_permission(current_user, comment, "delete")

    comment = await repositories.comment.remove(db, id=comment_id)
    return comment