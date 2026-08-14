from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.site_audits import get_site_analyzer
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.site_analyzer.analyzer import SiteAnalysisResult


class FakeAnalyzer:
    def analyze(self, url: str) -> SiteAnalysisResult:
        return SiteAnalysisResult(
            requested_url=url,
            final_url=url,
            http_status=200,
            score=82,
            confidence=0.91,
            score_version="ai-discoverability-v1",
            signals={"public_http_ok": True, "indexable": True},
            evidence={"page_title": "Clínica Demo"},
            blockers=(),
            recommendations=("Adicionar dados estruturados JSON-LD quando úteis.",),
        )


def test_create_and_read_site_audit() -> None:
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
    app.dependency_overrides[get_site_analyzer] = lambda: FakeAnalyzer()

    try:
        client = TestClient(app)
        response = client.post(
            "/site-audits",
            json={"url": "https://clinic.example/"},
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["score"] == 82
        assert payload["score_version"] == "ai-discoverability-v1"
        assert payload["evidence"]["page_title"] == "Clínica Demo"

        stored = client.get(f"/site-audits/{payload['id']}")
        assert stored.status_code == 200
        assert stored.json()["requested_url"] == "https://clinic.example/"
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
