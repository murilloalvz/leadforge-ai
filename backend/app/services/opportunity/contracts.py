from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol


class FindingCertainty(StrEnum):
    CONFIRMED = "confirmed"
    STRONG_SIGNAL = "strong_signal"
    INFERENCE = "inference"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class OpportunityFinding:
    key: str
    title: str
    certainty: FindingCertainty
    detail: str
    contribution: int
    evidence_keys: tuple[str, ...] = ()


@dataclass(frozen=True)
class OpportunityAssessmentResult:
    service_category: str
    score: int
    confidence: float
    version: str
    summary: str
    recommended_service: str | None
    findings: tuple[OpportunityFinding, ...]


@dataclass(frozen=True)
class OpportunityContext:
    signals: dict[str, bool | None]
    evidence: dict[str, Any]


class OpportunityModule(Protocol):
    service_category: str

    def assess(self, context: OpportunityContext) -> OpportunityAssessmentResult: ...
