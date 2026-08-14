from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from typing import Any, Literal

from app.models.discovery import DiscoveryCandidate, DiscoveryRun

ExportFormat = Literal["csv", "json"]
EXPORT_SCHEMA_VERSION = "discovery-export-v1"

CSV_FIELDS = (
    "run_id",
    "rank",
    "prospect_id",
    "name",
    "niche",
    "city",
    "state",
    "website",
    "phone",
    "source_url",
    "source_category",
    "priority_bucket",
    "service_category",
    "opportunity_score",
    "opportunity_confidence",
    "opportunity_version",
    "opportunity_summary",
    "recommended_service",
    "confirmed_findings_count",
    "unknown_findings_count",
    "confirmed_findings",
    "findings_json",
    "site_audit_id",
    "site_signals_json",
    "site_evidence_json",
    "ai_discoverability_score",
    "ai_discoverability_confidence",
)


@dataclass(frozen=True)
class DiscoveryExport:
    content: bytes
    media_type: str
    filename: str


def build_discovery_export(run: DiscoveryRun, export_format: ExportFormat) -> DiscoveryExport:
    if export_format == "json":
        content = json.dumps(
            _run_payload(run),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        return DiscoveryExport(
            content=content,
            media_type="application/json",
            filename=f"leadforge-discovery-{run.id}.json",
        )

    if export_format == "csv":
        return DiscoveryExport(
            content=_render_csv(run),
            media_type="text/csv",
            filename=f"leadforge-discovery-{run.id}.csv",
        )

    raise ValueError(f"Formato de exportação não suportado: {export_format}")


def _run_payload(run: DiscoveryRun) -> dict[str, Any]:
    candidates = sorted(run.candidates, key=lambda candidate: candidate.rank)
    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "run": {
            "id": run.id,
            "niche": run.niche,
            "city": run.city,
            "state": run.state,
            "provider": run.provider,
            "status": run.status,
            "requested_limit": run.requested_limit,
            "analyze_sites": run.analyze_sites,
            "site_audit_limit": run.site_audit_limit,
            "discovered_count": run.discovered_count,
            "created_count": run.created_count,
            "reused_count": run.reused_count,
            "audited_count": run.audited_count,
            "audit_failure_count": run.audit_failure_count,
            "created_at": _iso(run.created_at),
            "completed_at": _iso(run.completed_at),
        },
        "candidates": [_candidate_payload(candidate) for candidate in candidates],
    }


def _candidate_payload(candidate: DiscoveryCandidate) -> dict[str, Any]:
    prospect = candidate.prospect
    assessment = candidate.opportunity_assessment
    audit = candidate.site_audit

    opportunity = None
    if assessment is not None:
        opportunity = {
            "id": assessment.id,
            "service_category": assessment.service_category,
            "score": assessment.score,
            "confidence": assessment.confidence,
            "version": assessment.version,
            "summary": assessment.summary,
            "recommended_service": assessment.recommended_service,
            "findings": assessment.findings,
            "created_at": _iso(assessment.created_at),
        }

    site_audit = None
    if audit is not None:
        site_audit = {
            "id": audit.id,
            "requested_url": audit.requested_url,
            "final_url": audit.final_url,
            "http_status": audit.http_status,
            "signals": audit.signals,
            "evidence": audit.evidence,
            "created_at": _iso(audit.created_at),
        }

    return {
        "rank": candidate.rank,
        "priority_bucket": candidate.priority_bucket,
        "prospect": {
            "id": prospect.id,
            "name": prospect.name,
            "niche": prospect.niche,
            "city": prospect.city,
            "state": prospect.state,
            "website": prospect.website,
            "phone": prospect.phone,
        },
        "source": {
            "url": candidate.source_url,
            "category": candidate.source_category,
        },
        "opportunity": opportunity,
        "site_audit": site_audit,
        "ai_discoverability": {
            "score": candidate.ai_discoverability_score,
            "confidence": candidate.ai_discoverability_confidence,
        },
    }


def _render_csv(run: DiscoveryRun) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()

    for candidate in sorted(run.candidates, key=lambda item: item.rank):
        writer.writerow(_csv_row(run, candidate))

    return ("\ufeff" + stream.getvalue()).encode("utf-8")


def _csv_row(run: DiscoveryRun, candidate: DiscoveryCandidate) -> dict[str, str | int | float]:
    prospect = candidate.prospect
    assessment = candidate.opportunity_assessment
    audit = candidate.site_audit
    findings = assessment.findings if assessment is not None else []
    confirmed = [item for item in findings if item.get("certainty") == "confirmed"]
    unknown = [item for item in findings if item.get("certainty") == "unknown"]

    row: dict[str, str | int | float | None] = {
        "run_id": run.id,
        "rank": candidate.rank,
        "prospect_id": prospect.id,
        "name": prospect.name,
        "niche": prospect.niche,
        "city": prospect.city,
        "state": prospect.state,
        "website": prospect.website,
        "phone": prospect.phone,
        "source_url": candidate.source_url,
        "source_category": candidate.source_category,
        "priority_bucket": candidate.priority_bucket,
        "service_category": assessment.service_category if assessment else None,
        "opportunity_score": assessment.score if assessment else None,
        "opportunity_confidence": assessment.confidence if assessment else None,
        "opportunity_version": assessment.version if assessment else None,
        "opportunity_summary": assessment.summary if assessment else None,
        "recommended_service": assessment.recommended_service if assessment else None,
        "confirmed_findings_count": len(confirmed),
        "unknown_findings_count": len(unknown),
        "confirmed_findings": " | ".join(str(item.get("title", "")) for item in confirmed),
        "findings_json": _compact_json(findings),
        "site_audit_id": audit.id if audit else None,
        "site_signals_json": _compact_json(audit.signals if audit else {}),
        "site_evidence_json": _compact_json(audit.evidence if audit else {}),
        "ai_discoverability_score": candidate.ai_discoverability_score,
        "ai_discoverability_confidence": candidate.ai_discoverability_confidence,
    }
    return {key: _csv_safe(value) for key, value in row.items()}


def _compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _csv_safe(value: str | int | float | None) -> str | int | float:
    if value is None:
        return ""
    if not isinstance(value, str):
        return value

    stripped = value.lstrip()
    if stripped.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _iso(value: Any) -> str | None:
    return value.isoformat() if value is not None else None
