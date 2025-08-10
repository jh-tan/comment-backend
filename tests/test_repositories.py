import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.comment_history_repository import CommentHistoryRepository
from app.schemas.user import UserCreate
from app.schemas.comment import CommentCreate, CommentUpdate
from app.models.user import User
from app.models.comment import Comment
from app.models.comment_history import CommentHistory


class TestUserRepository:
    @pytest.fixture
    def user_repo(self):
        return UserRepository(User)
    
    async def test_create_user(self, db_session: AsyncSession, user_repo: UserRepository):
        user_data = UserCreate(
            username="newuser",
            password="newpassword",
            group="newgroup"
        )
        
        user = await user_repo.create(db_session, obj_in=user_data)
        
        assert user.username == "newuser"
        assert user.group == "newgroup"
        assert user.hashed_password is not None
    
    async def test_get_by_username(self, db_session: AsyncSession, user_repo: UserRepository, test_user: User):
        user = await user_repo.get_by_username(db_session, username=test_user.username)
        
        assert user is not None
        assert user.username == test_user.username
        assert user.id == test_user.id
    
    async def test_get_by_username_not_found(self, db_session: AsyncSession, user_repo: UserRepository):
        user = await user_repo.get_by_username(db_session, username="nonexistent")
        
        assert user is None
    
    async def test_authenticate_success(self, db_session: AsyncSession, user_repo: UserRepository, test_user: User):
        user = await user_repo.authenticate(db_session, username=test_user.username, password="testpassword")
        
        assert user is not None
        assert user.username == test_user.username
    
    async def test_authenticate_wrong_password(self, db_session: AsyncSession, user_repo: UserRepository, test_user: User):
        user = await user_repo.authenticate(db_session, username=test_user.username, password="wrongpassword")
        
        assert user is None
    
    async def test_authenticate_wrong_username(self, db_session: AsyncSession, user_repo: UserRepository):
        user = await user_repo.authenticate(db_session, username="wronguser", password="testpassword")
        
        assert user is None


class TestCommentRepository:
    @pytest.fixture
    def comment_repo(self):
        return CommentRepository(Comment)
    
    async def test_create_with_user(self, db_session: AsyncSession, comment_repo: CommentRepository, test_user: User):
        comment_data = CommentCreate(content="Test comment content")
        
        comment = await comment_repo.create_with_user(
            db_session, obj_in=comment_data, user_id=test_user.id
        )
        
        assert comment.content == "Test comment content"
        assert comment.user_id == test_user.id
    
    async def test_get_by_user(self, db_session: AsyncSession, comment_repo: CommentRepository, test_comment: Comment):
        comments = await comment_repo.get_by_user(
            db_session, user_id=test_comment.user_id
        )
        
        assert len(comments) == 1
        assert comments[0].id == test_comment.id
        assert comments[0].content == test_comment.content
    
    async def test_get_by_user_group(self, db_session: AsyncSession, comment_repo: CommentRepository, test_comment: Comment, test_user: User):
        comments = await comment_repo.get_by_user_group(
            db_session, user_group=test_user.group
        )
        
        assert len(comments) == 1
        assert comments[0].id == test_comment.id
    
    async def test_update_comment(self, db_session: AsyncSession, comment_repo: CommentRepository, test_comment: Comment):
        update_data = CommentUpdate(content="Updated comment content")
        
        updated_comment = await comment_repo.update(
            db_session, db_obj=test_comment, obj_in=update_data
        )
        
        assert updated_comment.content == "Updated comment content"
        assert updated_comment.id == test_comment.id


class TestCommentHistoryRepository:
    @pytest.fixture
    def history_repo(self):
        return CommentHistoryRepository(CommentHistory)
    
    async def test_create_history_entry(self, db_session: AsyncSession, history_repo: CommentHistoryRepository, test_comment: Comment):
        history = await history_repo.create_history_entry(
            db_session,
            comment_id=test_comment.id,
            old_value="Old content",
            new_value="New content"
        )
        
        assert history.comment_id == test_comment.id
        assert history.old_value == "Old content"
        assert history.new_value == "New content"
    
    async def test_get_by_comment(self, db_session: AsyncSession, history_repo: CommentHistoryRepository, test_comment_history: CommentHistory):
        histories = await history_repo.get_by_comment(
            db_session, comment_id=test_comment_history.comment_id
        )
        
        assert len(histories) == 1
        assert histories[0].id == test_comment_history.id
        assert histories[0].comment_id == test_comment_history.comment_id