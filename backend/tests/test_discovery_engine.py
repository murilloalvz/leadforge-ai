from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryQuery
from app.services.discovery.engine import DiscoveryEngine
from app.services.discovery.providers import MockDiscoveryProvider
from app.services.site_analyzer.analyzer import SiteAnalysisResult


class FakeAnalyzer:
    def analyze(self, url: str) -> SiteAnalysisResult:
        return SiteAnalysisResult(
            requested_url=url,
            final_url=url,
            http_status=200,
            score=42,
            confidence=0.9,
            score_version="ai-discoverability-v1",
            signals={
                "public_http_ok": True,
                "indexable": True,
                "important_content_textual": True,
                "business_identity_clear": True,
                "services_clearly_described": False,
                "location_clearly_described": False,
                "descriptive_titles": True,
                "structured_data_present": False,
                "local_business_schema": False,
            },
            evidence={"page_title": "Clínica Teste"},
            blockers=(),
            recommendations=("Melhorar descrição dos serviços.",),
        )


def _session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_discovery_creates_ranked_candidates_and_reuses_prospects() -> None:
    businesses = (
        DiscoveredBusiness(
            external_id="mock/1",
            name="Clínica Forte",
            category="beauty",
            city="Campinas",
            state="SP",
            website="https://forte.example",
            phone="+55 19 3000-0001",
            whatsapp="+55 19 99000-0001",
            source_url="https://source.example/1",
        ),
        DiscoveredBusiness(
            external_id="mock/2",
            name="Clínica Básica",
            category="beauty",
            city="Campinas",
            state="SP",
            phone="+55 19 3000-0002",
            source_url="https://source.example/2",
        ),
    )
    provider = MockDiscoveryProvider(businesses)
    discovery = DiscoveryEngine(provider, site_analyzer=FakeAnalyzer())
    sessions = _session_factory()
    query = DiscoveryQuery(
        niche="clínicas de estética",
        city="Campinas",
        state="SP",
        limit=10,
    )

    with sessions() as db:
        first = discovery.run(db, query, analyze_sites=True, site_audit_limit=1)
        assert first.run.discovered_count == 2
        assert first.run.created_count == 2
        assert first.run.reused_count == 0
        assert first.run.audited_count == 1

        top = first.candidates[0]
        assert top.priority_bucket == "medium_opportunity"
        assert top.rank == 1
        assert top.opportunity_assessment is not None
        assert top.opportunity_assessment.service_category == "web_development"
        assert top.opportunity_assessment.score == 40
        assert top.opportunity_assessment.confidence == 1.0

        # Legacy diagnostics remain persisted while the generic model is introduced.
        assert top.automation_score == 38
        assert top.ai_discoverability_score == 42

        second = discovery.run(db, query, analyze_sites=False, site_audit_limit=0)
        assert second.run.created_count == 0
        assert second.run.reused_count == 2
        assert all(
            candidate.priority_bucket == "insufficient_evidence"
            for candidate in second.candidates
        )
