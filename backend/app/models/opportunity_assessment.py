from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.entities import utcnow


class OpportunityAssessment(Base):
    __tablename__ = "opportunity_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(
        ForeignKey("prospects.id", ondelete="CASCADE"),
        index=True,
    )
    discovery_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("discovery_runs.id", ondelete="SET NULL"),
        index=True,
    )
    site_audit_id: Mapped[int | None] = mapped_column(
        ForeignKey("site_audits.id", ondelete="SET NULL"),
        index=True,
    )
    service_category: Mapped[str] = mapped_column(String(80), index=True)
    score: Mapped[int] = mapped_column(Integer, index=True)
    confidence: Mapped[float] = mapped_column(Float)
    version: Mapped[str] = mapped_column(String(80), index=True)
    summary: Mapped[str] = mapped_column(Text)
    recommended_service: Mapped[str | None] = mapped_column(String(240))
    findings: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True,
    )

    prospect = relationship("Prospect")
    discovery_run = relationship("DiscoveryRun")
    site_audit = relationship("SiteAudit")
