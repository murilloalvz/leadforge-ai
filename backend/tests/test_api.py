from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)
with TestingSession() as db:
    seed_database(db, reset=True)


def override_get_db() -> Generator[Session, None, None]:
    with TestingSession() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_prospects_returns_seeded_data() -> None:
    response = client.get("/prospects?min_score=50")
    assert response.status_code == 200
    body = response.json()
    assert body
    assert all(item["score"] >= 50 for item in body)
    assert all(item["is_fictional"] is True for item in body)
    assert all(item["score_version"] == "automation-v1.1" for item in body)


def test_list_prospects_supports_pagination() -> None:
    first_page = client.get("/prospects?limit=2&offset=0").json()
    second_page = client.get("/prospects?limit=2&offset=2").json()
    assert len(first_page) == 2
    assert len(second_page) == 2
    assert {item["id"] for item in first_page}.isdisjoint(
        {item["id"] for item in second_page}
    )


def test_get_prospect_includes_evidence_and_score_components() -> None:
    prospect_id = client.get("/prospects").json()[0]["id"]
    response = client.get(f"/prospects/{prospect_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["evidence"]
    assert payload["score_components"]
    assert payload["score_explanation"]
