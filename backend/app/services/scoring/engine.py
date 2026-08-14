from dataclasses import dataclass
from typing import Any

from app.services.scoring.rules import (
    COVERAGE_PREREQUISITES,
    COVERAGE_WEIGHTS,
    RULES,
    SCORE_VERSION,
)


@dataclass(frozen=True)
class ScoreComponentResult:
    signal: str
    value: Any
    weight: int
    contribution: int
    rationale: str


@dataclass(frozen=True)
class ScoreResult:
    total: int
    confidence: float
    components: tuple[ScoreComponentResult, ...]
    explanation: str
    version: str = SCORE_VERSION


class OpportunityScorer:
    def score(self, signals: dict[str, Any]) -> ScoreResult:
        self._validate(signals)
        components: list[ScoreComponentResult] = []
        raw_total = 0

        for rule in RULES:
            if not rule.predicate(signals):
                continue
            raw_total += rule.weight
            value = {key: signals.get(key) for key in rule.evidence_keys}
            components.append(
                ScoreComponentResult(
                    signal=rule.signal,
                    value=value,
                    weight=rule.weight,
                    contribution=rule.weight,
                    rationale=rule.rationale,
                )
            )

        total = max(0, min(100, raw_total))
        confidence = self._confidence(signals)
        explanation = self._explanation(total, confidence, components)
        return ScoreResult(
            total=total,
            confidence=confidence,
            components=tuple(components),
            explanation=explanation,
        )

    @staticmethod
    def _validate(signals: dict[str, Any]) -> None:
        invalid = [
            key
            for key in COVERAGE_WEIGHTS
            if key in signals
            and signals[key] is not None
            and not isinstance(signals[key], bool)
        ]
        if invalid:
            joined = ", ".join(sorted(invalid))
            raise ValueError(f"Sinais booleanos com valores inválidos: {joined}")

    @staticmethod
    def _is_observed(key: str, signals: dict[str, Any]) -> bool:
        if key not in signals or signals[key] is None:
            return False
        prerequisite = COVERAGE_PREREQUISITES.get(key)
        if prerequisite is not None and signals.get(prerequisite) is not True:
            return False
        return True

    @classmethod
    def _confidence(cls, signals: dict[str, Any]) -> float:
        total_weight = sum(COVERAGE_WEIGHTS.values())
        observed_weight = sum(
            weight
            for key, weight in COVERAGE_WEIGHTS.items()
            if cls._is_observed(key, signals)
        )
        if total_weight == 0:
            return 0.0
        return round(min(1.0, observed_weight / total_weight), 2)

    @staticmethod
    def _explanation(
        total: int,
        confidence: float,
        components: list[ScoreComponentResult],
    ) -> str:
        positive = [component.signal for component in components if component.contribution > 0]
        negative = [component.signal for component in components if component.contribution < 0]
        parts = [f"Score {total}/100 com confiança {confidence:.2f}."]
        if positive:
            parts.append("Sinais favoráveis: " + ", ".join(positive) + ".")
        if negative:
            parts.append("Redutores: " + ", ".join(negative) + ".")
        if not components:
            parts.append("Não há evidência suficiente para pontuar oportunidades.")
        return " ".join(parts)
