from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.discovery import DiscoveryCandidate, DiscoveryRun
from app.models.entities import Evidence, Prospect, ScoreComponent, utcnow
from app.models.opportunity_assessment import OpportunityAssessment
from app.models.site_audit import SiteAudit
from app.services.discovery.contracts import (
    DiscoveredBusiness,
    DiscoveryProvider,
    DiscoveryQuery,
)
from app.services.discovery.providers import DiscoveryProviderError
from app.services.opportunity import OpportunityContext, OpportunityModule
from app.services.opportunity.web_development import WebDevelopmentOpportunityModule
from app.services.prospect_identity import build_prospect_dedup_key
from app.services.scoring.engine import OpportunityScorer, ScoreResult
from app.services.site_analyzer import SiteAnalyzer, SiteFetchError, UnsafeURL


@dataclass(frozen=True)
class DiscoveryRunResult:
    run: DiscoveryRun
    candidates: tuple[DiscoveryCandidate, ...]


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


def _medium_high_ticket_signal(niche: str) -> bool | None:
    normalized = _normalize(niche)
    if any(term in normalized for term in ("estetica", "aesthetic", "beauty")):
        return True
    return None


def _commercial_signals(business: DiscoveredBusiness, niche: str) -> dict[str, bool]:
    """Legacy automation signals kept while the generic opportunity model is introduced."""
    signals: dict[str, bool] = {}
    if business.website:
        signals["website_present"] = True
    if business.whatsapp:
        signals["whatsapp_present"] = True
    channels = sum(bool(value) for value in (business.website, business.phone, business.whatsapp))
    if channels >= 2:
        signals["multiple_contact_channels"] = True
    ticket_signal = _medium_high_ticket_signal(niche)
    if ticket_signal is not None:
        signals["medium_high_ticket_vertical"] = ticket_signal
    return signals


def _priority_bucket(assessment: OpportunityAssessment | None) -> str:
    if assessment is None or assessment.confidence < 0.5:
        return "insufficient_evidence"
    if assessment.score >= 60:
        return "high_opportunity"
    if assessment.score >= 30:
        return "medium_opportunity"
    return "low_opportunity"


def _rank_key(candidate: DiscoveryCandidate) -> tuple[int, int, float, int]:
    bucket_order = {
        "high_opportunity": 0,
        "medium_opportunity": 1,
        "low_opportunity": 2,
        "insufficient_evidence": 3,
    }
    assessment = candidate.opportunity_assessment
    score = assessment.score if assessment is not None else -1
    confidence = assessment.confidence if assessment is not None else 0.0
    return (
        bucket_order.get(candidate.priority_bucket, 9),
        -score,
        -confidence,
        candidate.prospect_id,
    )


class DiscoveryEngine:
    def __init__(
        self,
        provider: DiscoveryProvider,
        *,
        site_analyzer: SiteAnalyzer | None = None,
        scorer: OpportunityScorer | None = None,
        opportunity_module: OpportunityModule | None = None,
    ) -> None:
        self.provider = provider
        self.site_analyzer = site_analyzer or SiteAnalyzer()
        self.scorer = scorer or OpportunityScorer()
        self.opportunity_module = opportunity_module or WebDevelopmentOpportunityModule()

    def run(
        self,
        db: Session,
        query: DiscoveryQuery,
        *,
        analyze_sites: bool = True,
        site_audit_limit: int = 5,
    ) -> DiscoveryRunResult:
        audit_budget = max(0, min(site_audit_limit, query.limit))
        run = DiscoveryRun(
            niche=query.niche,
            city=query.city,
            state=query.state.upper(),
            provider=self.provider.name,
            requested_limit=query.limit,
            analyze_sites=analyze_sites,
            site_audit_limit=audit_budget,
        )
        db.add(run)
        db.flush()

        try:
            businesses = self.provider.discover(query)
        except DiscoveryProviderError as exc:
            run.status = "failed"
            run.error_message = str(exc)
            run.completed_at = utcnow()
            db.commit()
            raise

        run.discovered_count = len(businesses)
        candidates: list[DiscoveryCandidate] = []
        seen_prospects: set[str] = set()
        audit_attempts = 0

        for business in businesses:
            candidate_key = build_prospect_dedup_key(
                business.name,
                business.city,
                business.state,
            )
            if candidate_key in seen_prospects:
                continue
            seen_prospects.add(candidate_key)

            prospect, created = self._upsert_prospect(db, query, business)
            if created:
                run.created_count += 1
            else:
                run.reused_count += 1

            automation = self.scorer.score(_commercial_signals(business, query.niche))
            self._maybe_update_legacy_prospect_score(db, prospect, automation)
            self._record_discovery_evidence(db, prospect, business, automation)

            site_audit: SiteAudit | None = None
            assessment: OpportunityAssessment | None = None
            if analyze_sites and business.website and audit_attempts < audit_budget:
                audit_attempts += 1
                try:
                    site_audit = self._analyze_site(db, prospect, business.website)
                    assessment = self._assess_opportunity(db, run, prospect, site_audit)
                    run.audited_count += 1
                except (SiteFetchError, UnsafeURL):
                    run.audit_failure_count += 1

            ai_score = site_audit.score if site_audit else None
            ai_confidence = site_audit.confidence if site_audit else None
            bucket = _priority_bucket(assessment)

            candidate = DiscoveryCandidate(
                run_id=run.id,
                prospect_id=prospect.id,
                site_audit_id=site_audit.id if site_audit else None,
                opportunity_assessment_id=assessment.id if assessment else None,
                opportunity_assessment=assessment,
                source_external_id=business.external_id,
                source_url=business.source_url,
                source_category=business.category,
                source_payload=business.raw,
                automation_score=automation.total,
                automation_confidence=automation.confidence,
                ai_discoverability_score=ai_score,
                ai_discoverability_confidence=ai_confidence,
                priority_bucket=bucket,
                rank=0,
            )
            db.add(candidate)
            candidates.append(candidate)

        ordered = sorted(candidates, key=_rank_key)
        for rank, candidate in enumerate(ordered, start=1):
            candidate.rank = rank

        run.status = "completed"
        run.completed_at = utcnow()
        db.commit()
        db.refresh(run)
        return DiscoveryRunResult(run=run, candidates=tuple(ordered))

    @staticmethod
    def _upsert_prospect(
        db: Session,
        query: DiscoveryQuery,
        business: DiscoveredBusiness,
    ) -> tuple[Prospect, bool]:
        dedup_key = build_prospect_dedup_key(business.name, business.city, business.state)
        prospect = db.scalar(select(Prospect).where(Prospect.dedup_key == dedup_key))
        if prospect is not None:
            if not prospect.website and business.website:
                prospect.website = business.website
            if not prospect.phone and business.phone:
                prospect.phone = business.phone
            return prospect, False

        prospect = Prospect(
            dedup_key=dedup_key,
            name=business.name,
            niche=query.niche,
            city=business.city,
            state=business.state.upper(),
            website=business.website,
            phone=business.phone,
            is_fictional=False,
        )
        db.add(prospect)
        db.flush()
        return prospect, True

    @staticmethod
    def _record_discovery_evidence(
        db: Session,
        prospect: Prospect,
        business: DiscoveredBusiness,
        automation: ScoreResult,
    ) -> None:
        source = business.source_url or "discovery-provider"
        db.add(
            Evidence(
                prospect_id=prospect.id,
                key="discovery_source",
                value={
                    "provider_external_id": business.external_id,
                    "category": business.category,
                },
                source=source,
                confidence=1.0,
            )
        )
        for component in automation.components:
            db.add(
                Evidence(
                    prospect_id=prospect.id,
                    key=component.signal,
                    value=component.value,
                    source=source,
                    confidence=1.0,
                )
            )

    @staticmethod
    def _maybe_update_legacy_prospect_score(
        db: Session,
        prospect: Prospect,
        result: ScoreResult,
    ) -> None:
        current_confidence = prospect.score_confidence or 0.0
        if prospect.score is not None and current_confidence > result.confidence:
            return

        prospect.score = result.total
        prospect.score_confidence = result.confidence
        prospect.score_version = result.version
        prospect.score_explanation = result.explanation
        db.execute(delete(ScoreComponent).where(ScoreComponent.prospect_id == prospect.id))
        for component in result.components:
            db.add(
                ScoreComponent(
                    prospect_id=prospect.id,
                    signal=component.signal,
                    value=component.value,
                    weight=component.weight,
                    contribution=component.contribution,
                    rationale=component.rationale,
                )
            )

    def _analyze_site(self, db: Session, prospect: Prospect, url: str) -> SiteAudit:
        result = self.site_analyzer.analyze(url)
        audit = SiteAudit(
            prospect_id=prospect.id,
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
        db.flush()
        return audit

    def _assess_opportunity(
        self,
        db: Session,
        run: DiscoveryRun,
        prospect: Prospect,
        site_audit: SiteAudit,
    ) -> OpportunityAssessment:
        result = self.opportunity_module.assess(
            OpportunityContext(signals=site_audit.signals, evidence=site_audit.evidence)
        )
        findings = [
            {
                **asdict(finding),
                "certainty": finding.certainty.value,
            }
            for finding in result.findings
        ]
        assessment = OpportunityAssessment(
            prospect_id=prospect.id,
            discovery_run_id=run.id,
            site_audit_id=site_audit.id,
            service_category=result.service_category,
            score=result.score,
            confidence=result.confidence,
            version=result.version,
            summary=result.summary,
            recommended_service=result.recommended_service,
            findings=findings,
        )
        db.add(assessment)
        db.flush()
        return assessment
