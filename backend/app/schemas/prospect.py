from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: Any
    source: str
    confidence: float
    observed_at: datetime


class ScoreComponentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    signal: str
    value: Any
    weight: int
    contribution: int
    rationale: str


class ProspectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    niche: str
    city: str
    state: str
    website: str | None
    status: str
    is_fictional: bool
    score: int | None
    score_confidence: float | None


class ProspectDetail(ProspectSummary):
    phone: str | None
    created_at: datetime
    updated_at: datetime
    evidence: list[EvidenceOut]
    score_components: list[ScoreComponentOut]
