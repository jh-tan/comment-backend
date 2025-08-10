from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.api import deps

async def get_context(db: AsyncSession = Depends(deps.get_db), current_user=Depends(deps.get_current_user)):
    return {
        "db": db,
        "current_user": current_user
    }
