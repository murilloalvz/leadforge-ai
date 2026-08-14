from dataclasses import dataclass
from typing import Any

from app.services.site_readiness.rules import (
    BLOCKER_CAPS,
    CRITERIA,
    SITE_READINESS_VERSION,
    TOTAL_WEIGHT,
)


@dataclass(frozen=True)
class ReadinessComponent:
    signal: str
    value: bool
    weight: int
    category: str
    rationale: str


@dataclass(frozen=True)
class SiteReadinessResult:
    score: int
    confidence: float
    components: tuple[ReadinessComponent, ...]
    blockers: tuple[str, ...]
    version: str = SITE_READINESS_VERSION


class AIDiscoverabilityScorer:
    """Measure discovery readiness, not probability of an AI recommendation."""

    def score(self, signals: dict[str, Any]) -> SiteReadinessResult:
        self._validate(signals)
        observed = [
            criterion
            for criterion in CRITERIA
            if signals.get(criterion.key) is not None
        ]
        observed_weight = sum(criterion.weight for criterion in observed)
        positive_weight = sum(
            criterion.weight
            for criterion in observed
            if signals.get(criterion.key) is True
        )

        score = 0 if observed_weight == 0 else round(100 * positive_weight / observed_weight)
        blockers = tuple(key for key in BLOCKER_CAPS if signals.get(key) is False)
        for blocker in blockers:
            score = min(score, BLOCKER_CAPS[blocker])

        confidence = 0.0 if TOTAL_WEIGHT == 0 else round(observed_weight / TOTAL_WEIGHT, 2)
        components = tuple(
            ReadinessComponent(
                signal=criterion.key,
                value=signals[criterion.key],
                weight=criterion.weight,
                category=criterion.category,
                rationale=criterion.rationale,
            )
            for criterion in observed
        )
        return SiteReadinessResult(
            score=score,
            confidence=confidence,
            components=components,
            blockers=blockers,
        )

    @staticmethod
    def _validate(signals: dict[str, Any]) -> None:
        known_keys = {criterion.key for criterion in CRITERIA}
        invalid = [
            key
            for key in known_keys
            if key in signals
            and signals[key] is not None
            and not isinstance(signals[key], bool)
        ]
        if invalid:
            joined = ", ".join(sorted(invalid))
            raise ValueError(f"Sinais booleanos com valores inválidos: {joined}")
