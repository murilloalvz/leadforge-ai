from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProspectStatus(StrEnum):
    DISCOVERED = "discovered"
    ANALYZED = "analyzed"
    HIGH_PRIORITY = "high_priority"
    OFFER_GENERATED = "offer_generated"
    DEMO_READY = "demo_ready"
    READY_FOR_REVIEW = "ready_for_review"
    CONTACTED = "contacted"
    REPLIED = "replied"
    MEETING = "meeting"
    PROPOSAL = "proposal"
    WON = "won"
    LOST = "lost"
    DO_NOT_CONTACT = "do_not_contact"


class Prospect(Base):
    __tablename__ = "prospects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    niche: Mapped[str] = mapped_column(String(120), index=True)
    city: Mapped[str] = mapped_column(String(120), index=True)
    state: Mapped[str] = mapped_column(String(2), index=True)
    website: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default=ProspectStatus.DISCOVERED.value, index=True)
    is_fictional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    score: Mapped[int | None] = mapped_column(Integer)
    score_confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    evidence: Mapped[list[Evidence]] = relationship(back_populates="prospect", cascade="all, delete-orphan")
    score_components: Mapped[list[ScoreComponent]] = relationship(back_populates="prospect", cascade="all, delete-orphan")
    opportunities: Mapped[list[Opportunity]] = relationship(back_populates="prospect", cascade="all, delete-orphan")
    outreach_drafts: Mapped[list[OutreachDraft]] = relationship(back_populates="prospect", cascade="all, delete-orphan")
    demos: Mapped[list[Demo]] = relationship(back_populates="prospect", cascade="all, delete-orphan")
    activities: Mapped[list[CRMActivity]] = relationship(back_populates="prospect", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[Any] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(String(500))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    prospect: Mapped[Prospect] = relationship(back_populates="evidence")


class ScoreComponent(Base):
    __tablename__ = "score_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), index=True)
    signal: Mapped[str] = mapped_column(String(120))
    value: Mapped[Any] = mapped_column(JSON)
    weight: Mapped[int] = mapped_column(Integer)
    contribution: Mapped[int] = mapped_column(Integer)
    rationale: Mapped[str] = mapped_column(Text)

    prospect: Mapped[Prospect] = relationship(back_populates="score_components")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(200))
    hypothesis: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(40), default="suggested")

    prospect: Mapped[Prospect] = relationship(back_populates="opportunities")


class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(40))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="awaiting_human_review")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    prospect: Mapped[Prospect] = relationship(back_populates="outreach_drafts")


class Demo(Base):
    __tablename__ = "demos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), index=True)
    template_key: Mapped[str] = mapped_column(String(120))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_fictional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    prospect: Mapped[Prospect] = relationship(back_populates="demos")


class CRMActivity(Base):
    __tablename__ = "crm_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), index=True)
    activity_type: Mapped[str] = mapped_column(String(80))
    from_status: Mapped[str | None] = mapped_column(String(40))
    to_status: Mapped[str | None] = mapped_column(String(40))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    prospect: Mapped[Prospect] = relationship(back_populates="activities")
