from datetime import datetime

from pydantic import BaseModel


class OpportunityFindingOut(BaseModel):
    key: str
    title: str
    certainty: str
    detail: str
    contribution: int
    evidence_keys: list[str]


class OpportunityAssessmentOut(BaseModel):
    id: int
    service_category: str
    score: int
    confidence: float
    version: str
    summary: str
    recommended_service: str | None
    findings: list[OpportunityFindingOut]
    created_at: datetime
