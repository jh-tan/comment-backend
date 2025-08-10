from app.models.user import User
from app.models.comment import Comment
from app.models.comment_history import CommentHistory
from app.graphql_api.models import UserType, CommentType, CommentHistoryType


def user_to_graphql(user: User) -> UserType:
    return UserType(
        id=user.id,
        username=user.username,
        group=user.group
    )


def comment_to_graphql(comment: Comment) -> CommentType:
    return CommentType(
        id=comment.id,
        content=comment.content,
        user_id=comment.user_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user=user_to_graphql(comment.user) if hasattr(comment, 'user') and comment.user else None
    )


def comment_history_to_graphql(history: CommentHistory) -> CommentHistoryType:
    return CommentHistoryType(
        id=history.id,
        comment_id=history.comment_id,
        timestamp=history.timestamp,
        old_value=history.old_value,
        new_value=history.new_value
    )