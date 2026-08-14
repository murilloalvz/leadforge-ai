from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

SignalValue = bool | None


@dataclass(frozen=True)
class CalibrationCase:
    case_id: str
    human_signals: Mapping[str, SignalValue]
    predicted_signals: Mapping[str, SignalValue]


@dataclass(frozen=True)
class CalibrationMetrics:
    labeled: int
    matched: int
    false_positive_gaps: int
    false_negative_gaps: int
    unknown_predictions: int

    @property
    def accuracy(self) -> float | None:
        if self.labeled == 0:
            return None
        return round(self.matched / self.labeled, 3)


@dataclass(frozen=True)
class SignalCalibration:
    signal: str
    metrics: CalibrationMetrics


@dataclass(frozen=True)
class CaseCalibration:
    case_id: str
    metrics: CalibrationMetrics


@dataclass(frozen=True)
class CalibrationReport:
    overall: CalibrationMetrics
    by_signal: tuple[SignalCalibration, ...]
    by_case: tuple[CaseCalibration, ...]


def evaluate_calibration(cases: Sequence[CalibrationCase]) -> CalibrationReport:
    by_case = tuple(
        CaseCalibration(
            case_id=case.case_id,
            metrics=_compare_signals(case.human_signals, case.predicted_signals),
        )
        for case in cases
    )

    signal_names = sorted(
        {
            signal
            for case in cases
            for signal, value in case.human_signals.items()
            if value is not None
        }
    )
    by_signal = tuple(
        SignalCalibration(
            signal=signal,
            metrics=_compare_signal_across_cases(signal, cases),
        )
        for signal in signal_names
    )
    overall = _sum_metrics(item.metrics for item in by_case)
    return CalibrationReport(overall=overall, by_signal=by_signal, by_case=by_case)


def _compare_signal_across_cases(
    signal: str,
    cases: Sequence[CalibrationCase],
) -> CalibrationMetrics:
    human = {case.case_id: case.human_signals.get(signal) for case in cases}
    predicted = {case.case_id: case.predicted_signals.get(signal) for case in cases}
    return _compare_signals(human, predicted)


def _compare_signals(
    human_signals: Mapping[str, SignalValue],
    predicted_signals: Mapping[str, SignalValue],
) -> CalibrationMetrics:
    labeled = 0
    matched = 0
    false_positive_gaps = 0
    false_negative_gaps = 0
    unknown_predictions = 0

    for signal, expected in human_signals.items():
        if expected is None:
            continue
        labeled += 1
        predicted = predicted_signals.get(signal)
        if predicted is None:
            unknown_predictions += 1
        elif predicted is expected:
            matched += 1
        elif predicted is False and expected is True:
            false_positive_gaps += 1
        elif predicted is True and expected is False:
            false_negative_gaps += 1

    return CalibrationMetrics(
        labeled=labeled,
        matched=matched,
        false_positive_gaps=false_positive_gaps,
        false_negative_gaps=false_negative_gaps,
        unknown_predictions=unknown_predictions,
    )


def _sum_metrics(metrics: Sequence[CalibrationMetrics] | object) -> CalibrationMetrics:
    values = tuple(metrics)  # type: ignore[arg-type]
    return CalibrationMetrics(
        labeled=sum(item.labeled for item in values),
        matched=sum(item.matched for item in values),
        false_positive_gaps=sum(item.false_positive_gaps for item in values),
        false_negative_gaps=sum(item.false_negative_gaps for item in values),
        unknown_predictions=sum(item.unknown_predictions for item in values),
    )
