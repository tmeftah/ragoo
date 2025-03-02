# Fixtures for testing
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ragoo.main import app
from ragoo.core.config import settings
from ragoo.database.database import Base, get_db
from ragoo.vectorestore.chroma_handler import ChromaHandler

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    # Create test user
    client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass",
        },
    )

    # Get auth token
    response = client.post(
        "/users/login", data={"username": "testuser", "password": "testpass"}
    )
    token = response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest.fixture()
def test_chroma_client(scope="session"):

    # Override config for tests
    settings.CHROMA_PERSIST_DIR = "./test_chroma_db"
    settings.CHROMA_COLLECTION_NAME = "test_collection"

    return ChromaHandler()
