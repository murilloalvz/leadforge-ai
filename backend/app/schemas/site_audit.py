from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SiteAuditRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2000)
    prospect_id: int | None = Field(default=None, gt=0)

    @field_validator("url")
    @classmethod
    def normalize_url(cls, value: str) -> str:
        return value.strip()


class SiteAuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    prospect_id: int | None
    requested_url: str
    final_url: str
    http_status: int
    score: int
    confidence: float
    score_version: str
    signals: dict[str, bool | None]
    evidence: dict[str, Any]
    blockers: list[str]
    recommendations: list[str]
    created_at: datetime
