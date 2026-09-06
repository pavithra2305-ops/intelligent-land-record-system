import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

TEST_DB_URL = "sqlite:///:memory:"
os.environ["DATABASE_URL"] = TEST_DB_URL
settings.DATABASE_URL = TEST_DB_URL

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch main database engine to point to test_engine
import app.core.database as app_db
app_db.engine = test_engine
app_db.SessionLocal = TestingSessionLocal

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models import User, District, Tehsil, Village, RoleEnum, LandRecord, Document, ValidationStatusEnum
from app.seed.seed_data import seed_database

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        # Run seed data on in-memory database
        seed_database()

        # Ensure test user accounts exist
        if not db.query(User).filter(User.email == "admin@test.com").first():
            db.add(User(email="admin@test.com", password_hash=get_password_hash("password123"), full_name="Test Admin", role=RoleEnum.ADMIN.value))
        if not db.query(User).filter(User.email == "verifier@test.com").first():
            db.add(User(email="verifier@test.com", password_hash=get_password_hash("password123"), full_name="Test Verifier", role=RoleEnum.VERIFIER.value))
        if not db.query(User).filter(User.email == "viewer@test.com").first():
            db.add(User(email="viewer@test.com", password_hash=get_password_hash("password123"), full_name="Test Viewer", role=RoleEnum.VIEWER.value))
        db.commit()

        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
