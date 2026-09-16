import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
# Tests override get_current_user entirely (see below), so this never needs
# to resolve to a real project - it just has to satisfy Settings' validation.
os.environ.setdefault("SUPABASE_URL", "https://test-project.supabase.co")

import pytest
from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.auth import get_current_user, CurrentUser
from app.main import app

# One shared in-memory SQLite connection for the whole test session, so tables
# created via Base.metadata.create_all persist across requests within a test.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


USER_A = "11111111-1111-1111-1111-111111111111"
USER_B = "22222222-2222-2222-2222-222222222222"


def _override_get_current_user(request: Request) -> CurrentUser:
    """
    IMPORTANT: app.dependency_overrides lives on the shared `app` object, not on
    any individual TestClient - so two client fixtures naively overriding
    get_current_user with different fixed users will stomp on each other the
    moment both are used in the same test (whichever fixture ran last wins for
    BOTH clients). That bug is exactly what test_non_member_cannot_log_workout
    caught the first time this was written.

    Instead we override it once, and read "who is this request from" out of a
    test-only header that each TestClient sets on itself - so each client keeps
    its own identity no matter what order fixtures are created in.
    """
    user_id = request.headers.get("x-test-user-id", USER_A)
    return CurrentUser(user_id=user_id, email=f"{user_id}@example.com")


@pytest.fixture
def current_user_id():
    return USER_A


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    with TestClient(app, headers={"x-test-user-id": USER_A}) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def other_user_client():
    """A second, different authenticated user - for testing authorization boundaries."""
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    with TestClient(app, headers={"x-test-user-id": USER_B}) as c:
        yield c
    app.dependency_overrides.clear()
