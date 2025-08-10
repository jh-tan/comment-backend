import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport 
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config.database import Base
from app.api.deps import get_db
from app.models.user import User
from app.models.comment import Comment
from app.models.comment_history import CommentHistory
from app.core.security import get_password_hash, create_access_token
from app import repositories


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    user_data = {
        "username": "testuser",
        "hashed_password": get_password_hash("testpassword"),
        "group": "testgroup"
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_2(db_session: AsyncSession) -> User:
    user_data = {
        "username": "testuser2",
        "hashed_password": get_password_hash("testpassword2"),
        "group": "testgroup2"
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    token = create_access_token(test_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_2(test_user_2: User) -> dict:
    token = create_access_token(test_user_2.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_comment(db_session: AsyncSession, test_user: User) -> Comment:
    comment_data = {
        "content": "This is a test comment",
        "user_id": test_user.id
    }
    comment = Comment(**comment_data)
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)
    return comment


@pytest.fixture
async def test_comment_history(db_session: AsyncSession, test_comment: Comment) -> CommentHistory:
    history_data = {
        "comment_id": test_comment.id,
        "old_value": None,
        "new_value": test_comment.content
    }
    history = CommentHistory(**history_data)
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)
    return history
