from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.discovery import DiscoveryCandidate, DiscoveryRun
from app.schemas.discovery import DiscoveryCandidateOut, DiscoveryRunOut, DiscoveryRunRequest
from app.schemas.opportunity import OpportunityAssessmentOut
from app.services.discovery.contracts import DiscoveryQuery
from app.services.discovery.engine import DiscoveryEngine
from app.services.discovery.factory import build_discovery_provider
from app.services.discovery.providers import DiscoveryProviderError

router = APIRouter(prefix="/discovery-runs", tags=["discovery"])
DbSession = Annotated[Session, Depends(get_db)]


def _opportunity_out(candidate: DiscoveryCandidate) -> OpportunityAssessmentOut | None:
    assessment = candidate.opportunity_assessment
    if assessment is None:
        return None
    return OpportunityAssessmentOut(
        id=assessment.id,
        service_category=assessment.service_category,
        score=assessment.score,
        confidence=assessment.confidence,
        version=assessment.version,
        summary=assessment.summary,
        recommended_service=assessment.recommended_service,
        findings=assessment.findings,
        created_at=assessment.created_at,
    )


def _candidate_out(candidate: DiscoveryCandidate) -> DiscoveryCandidateOut:
    prospect = candidate.prospect
    return DiscoveryCandidateOut(
        rank=candidate.rank,
        prospect_id=prospect.id,
        name=prospect.name,
        niche=prospect.niche,
        city=prospect.city,
        state=prospect.state,
        website=prospect.website,
        phone=prospect.phone,
        source_url=candidate.source_url,
        source_category=candidate.source_category,
        opportunity=_opportunity_out(candidate),
        priority_bucket=candidate.priority_bucket,
        site_audit_id=candidate.site_audit_id,
        ai_discoverability_score=candidate.ai_discoverability_score,
        ai_discoverability_confidence=candidate.ai_discoverability_confidence,
        automation_score=candidate.automation_score,
        automation_confidence=candidate.automation_confidence,
    )


def _run_out(run: DiscoveryRun) -> DiscoveryRunOut:
    ordered = sorted(run.candidates, key=lambda candidate: candidate.rank)
    return DiscoveryRunOut(
        id=run.id,
        niche=run.niche,
        city=run.city,
        state=run.state,
        provider=run.provider,
        status=run.status,
        requested_limit=run.requested_limit,
        analyze_sites=run.analyze_sites,
        site_audit_limit=run.site_audit_limit,
        discovered_count=run.discovered_count,
        created_count=run.created_count,
        reused_count=run.reused_count,
        audited_count=run.audited_count,
        audit_failure_count=run.audit_failure_count,
        error_message=run.error_message,
        created_at=run.created_at,
        completed_at=run.completed_at,
        candidates=[_candidate_out(candidate) for candidate in ordered],
    )


@router.post("", response_model=DiscoveryRunOut, status_code=status.HTTP_201_CREATED)
def create_discovery_run(payload: DiscoveryRunRequest, db: DbSession) -> DiscoveryRunOut:
    try:
        provider = build_discovery_provider(payload.provider)
        engine = DiscoveryEngine(provider)
        result = engine.run(
            db,
            DiscoveryQuery(
                niche=payload.niche,
                city=payload.city,
                state=payload.state,
                limit=payload.limit,
            ),
            analyze_sites=payload.analyze_sites,
            site_audit_limit=min(payload.site_audit_limit, payload.limit),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DiscoveryProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _run_out(result.run)


@router.get("/{run_id}", response_model=DiscoveryRunOut)
def get_discovery_run(run_id: int, db: DbSession) -> DiscoveryRunOut:
    run = db.get(DiscoveryRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Execução de discovery não encontrada")
    return _run_out(run)
