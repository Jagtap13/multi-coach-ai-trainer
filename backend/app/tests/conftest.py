import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "api"))

from fastapi import Header, HTTPException
from fastapi.testclient import TestClient
from database import Base, get_db
from auth_dependency import get_current_user
from user import User
from chat_history import ChatHistory
from progress import ProgressEntry
from workout_plan import WorkoutPlan
from feedback import MessageFeedback

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_user(db_session):
    user = User(email="test@example.com", hashed_password="notused")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session):
    user = User(email="other@example.com", hashed_password="notused")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client(db_session, test_user):
    import main

    def override_get_db():
        yield db_session

    def override_get_current_user(x_test_user: str | None = Header(None)):
        email = x_test_user or test_user.email
        user = db_session.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Test user not found")
        return user

    main.app.dependency_overrides[get_db] = override_get_db
    main.app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.clear()