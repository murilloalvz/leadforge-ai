from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


def test_create_and_read_discovery_run_with_mock_provider() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    def override_get_db():
        with testing_session() as db:
            yield db

    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)
        response = client.post(
            "/discovery-runs",
            json={
                "niche": "clínicas de estética",
                "city": "Campinas",
                "state": "sp",
                "provider": "mock",
                "limit": 10,
                "analyze_sites": False,
                "site_audit_limit": 0,
            },
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["status"] == "completed"
        assert payload["state"] == "SP"
        assert payload["discovered_count"] == 2
        assert len(payload["candidates"]) == 2
        assert payload["candidates"][0]["name"] == "Clínica Aurora Demo"
        assert payload["candidates"][0]["automation_score"] == 38

        stored = client.get(f"/discovery-runs/{payload['id']}")
        assert stored.status_code == 200
        assert stored.json()["discovered_count"] == 2
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
