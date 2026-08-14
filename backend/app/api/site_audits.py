from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Prospect
from app.models.site_audit import SiteAudit
from app.schemas.site_audit import SiteAuditOut, SiteAuditRequest
from app.services.site_analyzer import SiteAnalyzer, SiteFetchError, UnsafeURL

router = APIRouter(prefix="/site-audits", tags=["site-audits"])


def get_site_analyzer() -> SiteAnalyzer:
    return SiteAnalyzer()


DbSession = Annotated[Session, Depends(get_db)]
Analyzer = Annotated[SiteAnalyzer, Depends(get_site_analyzer)]


@router.post("", response_model=SiteAuditOut, status_code=status.HTTP_201_CREATED)
def create_site_audit(
    payload: SiteAuditRequest,
    db: DbSession,
    analyzer: Analyzer,
) -> SiteAudit:
    if payload.prospect_id is not None and db.get(Prospect, payload.prospect_id) is None:
        raise HTTPException(status_code=404, detail="Prospect não encontrado")

    try:
        result = analyzer.analyze(payload.url)
    except UnsafeURL as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SiteFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    audit = SiteAudit(
        prospect_id=payload.prospect_id,
        requested_url=result.requested_url,
        final_url=result.final_url,
        http_status=result.http_status,
        score=result.score,
        confidence=result.confidence,
        score_version=result.score_version,
        signals=result.signals,
        evidence=result.evidence,
        blockers=list(result.blockers),
        recommendations=list(result.recommendations),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


@router.get("/{audit_id}", response_model=SiteAuditOut)
def get_site_audit(audit_id: int, db: DbSession) -> SiteAudit:
    audit = db.get(SiteAudit, audit_id)
    if audit is None:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    return audit
