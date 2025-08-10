import strawberry
from typing import List
from app import repositories, schemas
from app.utils.permissions import ensure_comment_permission
from app.graphql_api.models import (
    UserType, CommentType, CommentHistoryType,
    UserInput, CommentInput, CommentUpdateInput
)
from app.graphql_api.converters import user_to_graphql, comment_to_graphql, comment_history_to_graphql


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info) -> List[UserType]:
        db = info.context["db"]
        users = await repositories.user.get_multi(db)
        return [user_to_graphql(u) for u in users]

    @strawberry.field
    async def comments(self, info) -> List[CommentType]:
        db = info.context["db"]
        current_user = info.context["current_user"]
        comments = await repositories.comment.get_by_user_group_with_user(db, user_group=current_user.group)
        return [comment_to_graphql(c) for c in comments]

    @strawberry.field
    async def comment_history(self, info, comment_id: int) -> List[CommentHistoryType]:
        db = info.context["db"]
        current_user = info.context["current_user"]
        
        comment = await repositories.comment.get(db, id=comment_id)
        if not comment:
            raise ValueError("Comment not found")
        
        ensure_comment_permission(current_user, comment, "read")
        
        history = await repositories.comment_history.get_by_comment(db, comment_id=comment_id)
        return [comment_history_to_graphql(h) for h in history]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, info, input: UserInput) -> UserType:
        db = info.context["db"]
        
        existing_user = await repositories.user.get_by_username(db, username=input.username)
        if existing_user:
            raise ValueError("User already exists")
        
        user = await repositories.user.create(
            db, 
            obj_in=schemas.UserCreate(
                username=input.username,
                password=input.password,
                group=input.group
            )
        )
        return user_to_graphql(user)

    @strawberry.mutation
    async def create_comment(self, info, input: CommentInput) -> CommentType:
        db = info.context["db"]
        current_user = info.context["current_user"]
        
        comment = await repositories.comment.create_with_user(
            db=db, 
            obj_in=schemas.CommentCreate(content=input.content), 
            user_id=current_user.id
        )
        
        await repositories.comment_history.create_history_entry(
            db=db, 
            comment_id=comment.id, 
            old_value=None, 
            new_value=comment.content
        )
        
        comment_with_user = await repositories.comment.get_with_user(db, id=comment.id)
        return comment_to_graphql(comment_with_user)

    @strawberry.mutation
    async def update_comment(self, info, comment_id: int, input: CommentUpdateInput) -> CommentType:
        db = info.context["db"]
        current_user = info.context["current_user"]
        
        comment = await repositories.comment.get(db, id=comment_id)
        if not comment:
            raise ValueError("Comment not found")
        
        ensure_comment_permission(current_user, comment, "update")
        
        old_content = comment.content
        
        update_data = {}
        if input.content is not None:
            update_data["content"] = input.content
            
        comment = await repositories.comment.update(db, db_obj=comment, obj_in=update_data)
        
        if input.content and input.content != old_content:
            await repositories.comment_history.create_history_entry(
                db=db, 
                comment_id=comment.id, 
                old_value=old_content, 
                new_value=comment.content
            )
        
        comment_with_user = await repositories.comment.get_with_user(db, id=comment.id)
        return comment_to_graphql(comment_with_user)