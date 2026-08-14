from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.opportunity import OpportunityAssessmentOut


class DiscoveryRunRequest(BaseModel):
    niche: str = Field(min_length=2, max_length=160)
    city: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=2)
    limit: int = Field(default=10, ge=1, le=30)
    provider: Literal["google_places", "openstreetmap", "mock"] = "google_places"
    analyze_sites: bool = True
    site_audit_limit: int = Field(default=5, ge=0, le=10)

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str) -> str:
        return value.upper()


class DiscoveryCandidateOut(BaseModel):
    rank: int
    prospect_id: int
    name: str
    niche: str
    city: str
    state: str
    website: str | None
    phone: str | None
    source_url: str | None
    source_category: str | None
    opportunity: OpportunityAssessmentOut | None
    priority_bucket: str
    site_audit_id: int | None
    ai_discoverability_score: int | None
    ai_discoverability_confidence: float | None
    automation_score: int
    automation_confidence: float


class DiscoveryRunOut(BaseModel):
    id: int
    niche: str
    city: str
    state: str
    provider: str
    status: str
    requested_limit: int
    analyze_sites: bool
    site_audit_limit: int
    discovered_count: int
    created_count: int
    reused_count: int
    audited_count: int
    audit_failure_count: int
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
    candidates: list[DiscoveryCandidateOut]
