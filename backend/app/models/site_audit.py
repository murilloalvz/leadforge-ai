from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.entities import utcnow


class SiteAudit(Base):
    __tablename__ = "site_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int | None] = mapped_column(
        ForeignKey("prospects.id", ondelete="SET NULL"),
        index=True,
    )
    requested_url: Mapped[str] = mapped_column(String(2000))
    final_url: Mapped[str] = mapped_column(String(2000))
    http_status: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer, index=True)
    confidence: Mapped[float] = mapped_column(Float)
    score_version: Mapped[str] = mapped_column(String(80), index=True)
    signals: Mapped[dict[str, Any]] = mapped_column(JSON)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON)
    blockers: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True,
    )

    prospect = relationship("Prospect")
