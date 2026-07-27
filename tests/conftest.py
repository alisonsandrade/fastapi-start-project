"""Shared pytest fixtures for the whole test suite.

This file is automatically discovered by pytest. Every fixture defined here
becomes available to any test module without needing an explicit import.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base
from app.core.dependencies.database import get_db
from app.users import service as user_service
from app.users.models import UserRole


# ---------------------------------------------------------------------------
# Test database configuration
# ---------------------------------------------------------------------------
# We use a dedicated SQLite database file so we never touch the real one.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# All routes are mounted under this prefix (see main.py). Centralizing it here
# means that if you ever bump the API version you only change ONE line.
API_PREFIX = "/api/v1"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ---------------------------------------------------------------------------
# Reusable test data
# ---------------------------------------------------------------------------
TEST_USER = {
    "name": "John Doe",
    "email": "john@example.com",
    "password": "StrongPassword123!",
}

TEST_ADMIN = {
    "name": "Admin User",
    "email": "admin@example.com",
    "password": "AdminPassword123!",
}


# ---------------------------------------------------------------------------
# Dependency override
# ---------------------------------------------------------------------------
def override_get_db():
    """Provide a database session bound to the TEST database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def client():
    """Return a TestClient with a fresh database for each test.

    Before every test we drop and recreate all tables, guaranteeing perfect
    isolation between tests (no data leaks from one test to another).
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Register the default TEST_USER and return its credentials."""
    client.post(
        f"{API_PREFIX}/auth/register",
        json=TEST_USER,
    )
    return TEST_USER


@pytest.fixture
def auth_headers(client, registered_user):
    """Log in as the default user and return ready-to-use auth headers."""
    response = client.post(
        f"{API_PREFIX}/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_user(client):
    """Create an ADMIN user directly through the service layer.

    The public /auth/register endpoint always creates MEMBER users, so the
    only way to get an ADMIN in the tests is to call the service directly.
    """
    db = TestingSessionLocal()
    try:
        user_service.create_user(
            db,
            name=TEST_ADMIN["name"],
            email=TEST_ADMIN["email"],
            password=TEST_ADMIN["password"],
            role=UserRole.ADMIN,
        )
    finally:
        db.close()
    return TEST_ADMIN


@pytest.fixture
def admin_headers(client, admin_user):
    """Log in as the ADMIN user and return ready-to-use auth headers."""
    response = client.post(
        f"{API_PREFIX}/auth/login",
        data={
            "username": admin_user["email"],
            "password": admin_user["password"],
        },
    )
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}
