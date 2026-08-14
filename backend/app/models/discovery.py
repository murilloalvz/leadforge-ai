from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.entities import utcnow


class DiscoveryRun(Base):
    __tablename__ = "discovery_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    niche: Mapped[str] = mapped_column(String(160), index=True)
    city: Mapped[str] = mapped_column(String(120), index=True)
    state: Mapped[str] = mapped_column(String(2), index=True)
    provider: Mapped[str] = mapped_column(String(80), index=True)
    requested_limit: Mapped[int] = mapped_column(Integer)
    analyze_sites: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    site_audit_limit: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[str] = mapped_column(String(40), default="running", index=True)
    discovered_count: Mapped[int] = mapped_column(Integer, default=0)
    created_count: Mapped[int] = mapped_column(Integer, default=0)
    reused_count: Mapped[int] = mapped_column(Integer, default=0)
    audited_count: Mapped[int] = mapped_column(Integer, default=0)
    audit_failure_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    candidates: Mapped[list[DiscoveryCandidate]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="DiscoveryCandidate.rank",
    )


class DiscoveryCandidate(Base):
    __tablename__ = "discovery_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("discovery_runs.id", ondelete="CASCADE"),
        index=True,
    )
    prospect_id: Mapped[int] = mapped_column(
        ForeignKey("prospects.id", ondelete="CASCADE"),
        index=True,
    )
    site_audit_id: Mapped[int | None] = mapped_column(
        ForeignKey("site_audits.id", ondelete="SET NULL"),
        index=True,
    )
    opportunity_assessment_id: Mapped[int | None] = mapped_column(
        ForeignKey("opportunity_assessments.id", ondelete="SET NULL"),
        index=True,
    )
    source_external_id: Mapped[str] = mapped_column(String(160))
    source_url: Mapped[str | None] = mapped_column(String(2000))
    source_category: Mapped[str | None] = mapped_column(String(300))
    source_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    automation_score: Mapped[int] = mapped_column(Integer)
    automation_confidence: Mapped[float] = mapped_column(Float)
    ai_discoverability_score: Mapped[int | None] = mapped_column(Integer)
    ai_discoverability_confidence: Mapped[float | None] = mapped_column(Float)
    priority_bucket: Mapped[str] = mapped_column(String(60), index=True)
    rank: Mapped[int] = mapped_column(Integer, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    run: Mapped[DiscoveryRun] = relationship(back_populates="candidates")
    prospect = relationship("Prospect")
    site_audit = relationship("SiteAudit")
    opportunity_assessment = relationship("OpportunityAssessment")
