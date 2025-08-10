from fastapi import APIRouter
from . import users, comments, comment_history, auth

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(comment_history.router, prefix="/users", tags=["comment-history"])

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "System is running"}