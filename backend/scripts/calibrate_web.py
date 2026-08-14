from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.services.opportunity.calibration import (
    CalibrationCase,
    CalibrationMetrics,
    evaluate_calibration,
)
from app.services.site_analyzer import SiteAnalyzer, SiteFetchError, UnsafeURL

DEFAULT_DATASET = (
    Path(__file__).resolve().parents[2] / "sample_data" / "web_calibration_v0.3.3.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa a calibração manual do módulo web contra sites públicos."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def metrics_payload(metrics: CalibrationMetrics) -> dict[str, Any]:
    payload = asdict(metrics)
    payload["accuracy"] = metrics.accuracy
    return payload


def run(dataset_path: Path) -> dict[str, Any]:
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    analyzer = SiteAnalyzer()
    cases: list[CalibrationCase] = []
    errors: list[dict[str, str]] = []

    for item in dataset["cases"]:
        case_id = str(item["id"])
        url = str(item["url"])
        try:
            analysis = analyzer.analyze(url)
        except (SiteFetchError, UnsafeURL) as exc:
            errors.append({"case_id": case_id, "url": url, "error": str(exc)})
            continue

        cases.append(
            CalibrationCase(
                case_id=case_id,
                human_signals=item["human_signals"],
                predicted_signals=analysis.signals,
            )
        )

    report = evaluate_calibration(cases)
    return {
        "dataset_version": dataset.get("dataset_version"),
        "analyzed_at": datetime.now(UTC).isoformat(),
        "successful_cases": len(cases),
        "failed_cases": len(errors),
        "overall": metrics_payload(report.overall),
        "by_signal": [
            {"signal": item.signal, **metrics_payload(item.metrics)}
            for item in report.by_signal
        ],
        "by_case": [
            {"case_id": item.case_id, **metrics_payload(item.metrics)}
            for item in report.by_case
        ],
        "errors": errors,
    }


def main() -> None:
    args = parse_args()
    payload = run(args.dataset)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(f"{rendered}\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
