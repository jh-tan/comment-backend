import asyncio

from app.config.database import AsyncSessionLocal
from app import repositories
from app.schemas.user import UserCreate
from app.schemas.comment import CommentCreate

async def seed_data():
    async with AsyncSessionLocal() as db: 
        users_data = [
            {"username": "admin", "password": "admin123", "group": "administrators"},
            {"username": "user1", "password": "user123", "group": "group1"},
            {"username": "user2", "password": "user456", "group": "group1"},
            {"username": "user3", "password": "user789", "group": "group2"},
            {"username": "user4", "password": "user101", "group": "group2"},
        ]

        created_users = []
        for user_data in users_data:
            existing_user = await repositories.user.get_by_username(db, username=user_data["username"])
            if not existing_user:
                user = await repositories.user.create(db, obj_in=UserCreate(**user_data))
                created_users.append(user)
                print(f"Created user: {user.username}")
            else:
                created_users.append(existing_user)

        comments_data = [
            {"content": "This is the first comment from admin", "user_id": created_users[0].id},
            {"content": "Hello from user1 in group1", "user_id": created_users[1].id},
            {"content": "Another comment from user2", "user_id": created_users[2].id},
            {"content": "User3 from group2 commenting", "user_id": created_users[3].id},
            {"content": "Final comment from user4", "user_id": created_users[4].id},
        ]

        for comment_data in comments_data:
            comment = await repositories.comment.create_with_user(
                db,
                obj_in=CommentCreate(content=comment_data["content"]),
                user_id=comment_data["user_id"]
            )

            await repositories.comment_history.create_history_entry(
                db=db,
                comment_id=comment.id,
                old_value=None,
                new_value=comment.content
            )
            print(f"Created comment: {comment.content[:30]}...")

        await db.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())