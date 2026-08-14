from app.services.opportunity.calibration import CalibrationCase, evaluate_calibration


def test_calibration_reports_gap_errors_and_unknowns() -> None:
    report = evaluate_calibration(
        (
            CalibrationCase(
                case_id="site-a",
                human_signals={
                    "cta": True,
                    "location": False,
                    "services": True,
                    "ignored": None,
                },
                predicted_signals={
                    "cta": True,
                    "location": True,
                    "services": False,
                },
            ),
            CalibrationCase(
                case_id="site-b",
                human_signals={
                    "cta": True,
                    "location": False,
                    "services": False,
                },
                predicted_signals={
                    "cta": None,
                    "location": False,
                    "services": False,
                },
            ),
        )
    )

    assert report.overall.labeled == 6
    assert report.overall.matched == 3
    assert report.overall.false_positive_gaps == 1
    assert report.overall.false_negative_gaps == 1
    assert report.overall.unknown_predictions == 1
    assert report.overall.accuracy == 0.5

    by_signal = {item.signal: item.metrics for item in report.by_signal}
    assert by_signal["cta"].matched == 1
    assert by_signal["cta"].unknown_predictions == 1
    assert by_signal["location"].false_negative_gaps == 1
    assert by_signal["services"].false_positive_gaps == 1


def test_calibration_with_no_human_labels_has_no_accuracy() -> None:
    report = evaluate_calibration(
        (
            CalibrationCase(
                case_id="unreviewed",
                human_signals={"cta": None},
                predicted_signals={"cta": False},
            ),
        )
    )

    assert report.overall.labeled == 0
    assert report.overall.accuracy is None
    assert report.by_signal == ()
