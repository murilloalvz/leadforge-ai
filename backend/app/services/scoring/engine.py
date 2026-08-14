from dataclasses import dataclass
from typing import Any

from app.services.scoring.rules import COVERAGE_WEIGHTS, RULES


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


class OpportunityScorer:
    def score(self, signals: dict[str, Any]) -> ScoreResult:
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
        return ScoreResult(total, confidence, tuple(components), explanation)

    @staticmethod
    def _confidence(signals: dict[str, Any]) -> float:
        total_weight = sum(COVERAGE_WEIGHTS.values())
        observed_weight = sum(
            weight for key, weight in COVERAGE_WEIGHTS.items() if key in signals and signals[key] is not None
        )
        if total_weight == 0:
            return 0.0
        return round(min(0.95, observed_weight / total_weight), 2)

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
