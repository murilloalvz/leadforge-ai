from contextlib import contextmanager
from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@contextmanager
def export_client() -> Iterator[TestClient]:
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
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def test_export_discovery_run_as_csv_and_json() -> None:
    with export_client() as client:
        created = client.post(
            "/discovery-runs",
            json={
                "niche": "clínicas de estética",
                "city": "Campinas",
                "state": "SP",
                "provider": "mock",
                "limit": 2,
                "analyze_sites": False,
                "site_audit_limit": 0,
            },
        )
        assert created.status_code == 201
        run_id = created.json()["id"]

        csv_response = client.get(f"/discovery-runs/{run_id}/export?format=csv")
        assert csv_response.status_code == 200
        assert csv_response.headers["content-type"].startswith("text/csv")
        assert (
            csv_response.headers["content-disposition"]
            == f'attachment; filename="leadforge-discovery-{run_id}.csv"'
        )
        assert "Clínica Aurora Demo" in csv_response.content.decode("utf-8-sig")

        json_response = client.get(f"/discovery-runs/{run_id}/export?format=json")
        assert json_response.status_code == 200
        assert json_response.headers["content-type"].startswith("application/json")
        payload = json_response.json()
        assert payload["schema_version"] == "discovery-export-v1"
        assert payload["run"]["id"] == run_id
        assert len(payload["candidates"]) == 2
        assert payload["candidates"][0]["rank"] == 1


def test_export_missing_discovery_run_returns_404() -> None:
    with export_client() as client:
        response = client.get("/discovery-runs/999/export?format=json")

    assert response.status_code == 404
    assert response.json()["detail"] == "Execução de discovery não encontrada"
