import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app import models

from app.database import Base, get_db
from main import app


TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/news_digest_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    """Creates clean bd before every test, then deletes."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with db changed to test"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_test_document_with_chunks(
    db_session,
    owner_id: id,
    title: str = "Test doc",
    chunks_data: list[tuple[str, list[float]]] | None = None,
) -> models.Document:
    if chunks_data is None:
        chunks_data = [
            ("First chunk about JWT tokens.", [0.1] * 1536),
            ("Second chunk about authentication.", [0.2] * 1536),
        ]
    doc = models.Document(
        title=title,
        content="dummy content",
        owner_id=owner_id,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    for i, (text, embedding) in enumerate(chunks_data):
        chunk = models.Chunk(
            document_id=doc.id,
            content=text,
            chunk_index=i,
            embedding=embedding,
        )
        db_session.add(chunk)
    db_session.commit()
    db_session.refresh(doc)

    return doc