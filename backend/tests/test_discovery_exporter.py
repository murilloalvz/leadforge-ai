import csv
import io
import json
from datetime import UTC, datetime

from app.models.discovery import DiscoveryCandidate, DiscoveryRun
from app.models.entities import Prospect
from app.models.opportunity_assessment import OpportunityAssessment
from app.models.site_audit import SiteAudit
from app.services.discovery.exporter import build_discovery_export


def _sample_run() -> DiscoveryRun:
    now = datetime(2026, 8, 14, 20, 0, tzinfo=UTC)
    prospect = Prospect(
        id=7,
        dedup_key="sample",
        name="=HYPERLINK(\"https://example.com\")",
        niche="clínica de estética",
        city="Campinas",
        state="SP",
        website="https://example.com",
        phone="+55 19 99999-9999",
        is_fictional=False,
        created_at=now,
        updated_at=now,
    )
    audit = SiteAudit(
        id=11,
        prospect_id=prospect.id,
        requested_url="https://example.com",
        final_url="https://example.com/",
        http_status=200,
        score=70,
        confidence=0.9,
        score_version="ai-discoverability-v1",
        signals={"action_cta_present": False, "https_enabled": True},
        evidence={"page_title": "Exemplo", "word_count": 220},
        blockers=[],
        recommendations=[],
        created_at=now,
    )
    assessment = OpportunityAssessment(
        id=13,
        prospect_id=prospect.id,
        discovery_run_id=3,
        site_audit_id=audit.id,
        service_category="web_development",
        score=55,
        confidence=0.92,
        version="web-development-v2",
        summary="Um gap objetivo foi confirmado.",
        recommended_service="Otimizações pontuais de site",
        findings=[
            {
                "key": "action_cta_present",
                "title": "Chamada para ação não identificada",
                "certainty": "confirmed",
                "detail": "Nenhuma CTA foi identificada na página analisada.",
                "contribution": 7,
                "evidence_keys": ["action_cta_present"],
            },
            {
                "key": "performance_score",
                "title": "Performance real",
                "certainty": "unknown",
                "detail": "Sem fonte adequada.",
                "contribution": 0,
                "evidence_keys": ["performance_score"],
            },
        ],
        created_at=now,
    )
    candidate = DiscoveryCandidate(
        id=17,
        run_id=3,
        prospect_id=prospect.id,
        site_audit_id=audit.id,
        opportunity_assessment_id=assessment.id,
        source_external_id="osm:123",
        source_url="https://www.openstreetmap.org/node/123",
        source_category="beauty",
        source_payload={},
        automation_score=20,
        automation_confidence=0.5,
        ai_discoverability_score=70,
        ai_discoverability_confidence=0.9,
        priority_bucket="medium_opportunity",
        rank=1,
        created_at=now,
    )
    candidate.prospect = prospect
    candidate.site_audit = audit
    candidate.opportunity_assessment = assessment

    run = DiscoveryRun(
        id=3,
        niche="clínicas de estética",
        city="Campinas",
        state="SP",
        provider="openstreetmap",
        requested_limit=10,
        analyze_sites=True,
        site_audit_limit=5,
        status="completed",
        discovered_count=1,
        created_count=1,
        reused_count=0,
        audited_count=1,
        audit_failure_count=0,
        created_at=now,
        completed_at=now,
    )
    run.candidates = [candidate]
    return run


def test_json_export_preserves_structured_opportunity_and_evidence() -> None:
    exported = build_discovery_export(_sample_run(), "json")
    payload = json.loads(exported.content)

    assert exported.filename == "leadforge-discovery-3.json"
    assert payload["schema_version"] == "discovery-export-v1"
    assert payload["run"]["provider"] == "openstreetmap"
    assert payload["candidates"][0]["opportunity"]["score"] == 55
    assert payload["candidates"][0]["opportunity"]["findings"][0]["certainty"] == "confirmed"
    assert payload["candidates"][0]["site_audit"]["signals"]["action_cta_present"] is False
    assert payload["candidates"][0]["site_audit"]["evidence"]["word_count"] == 220


def test_json_export_is_deterministic_for_same_run() -> None:
    run = _sample_run()

    first = build_discovery_export(run, "json").content
    second = build_discovery_export(run, "json").content

    assert first == second


def test_csv_export_flattens_findings_and_neutralizes_formula_cells() -> None:
    exported = build_discovery_export(_sample_run(), "csv")
    decoded = exported.content.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(decoded)))

    assert exported.filename == "leadforge-discovery-3.csv"
    assert len(rows) == 1
    row = rows[0]
    assert row["name"].startswith("'=HYPERLINK")
    assert row["opportunity_score"] == "55"
    assert row["confirmed_findings_count"] == "1"
    assert row["unknown_findings_count"] == "1"
    assert "Chamada para ação" in row["confirmed_findings"]
    assert json.loads(row["site_signals_json"])["https_enabled"] is True
    assert json.loads(row["findings_json"])[0]["certainty"] == "confirmed"
