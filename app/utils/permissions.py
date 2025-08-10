from fastapi import HTTPException, status
from app.models.user import User
from app.models.comment import Comment


def check_comment_permission(user: User, comment: Comment, action: str = "read") -> bool:
    if action == "read":
        return user.group == comment.user.group
    elif action in ["update", "delete"]:
        return user.id == comment.user_id
    return False


def ensure_comment_permission(user: User, comment: Comment, action: str = "read"):
    if not check_comment_permission(user, comment, action):
        if action == "read":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions. You can only access comments from users in your group."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions. You can only modify your own comments."
            )