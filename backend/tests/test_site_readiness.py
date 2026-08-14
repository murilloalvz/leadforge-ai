import pytest

from app.services.site_readiness.engine import AIDiscoverabilityScorer


def test_complete_ready_site_scores_100() -> None:
    signals = {
        "public_http_ok": True,
        "indexable": True,
        "googlebot_allowed": True,
        "oai_searchbot_allowed": True,
        "important_content_textual": True,
        "business_identity_clear": True,
        "services_clearly_described": True,
        "location_clearly_described": True,
        "descriptive_titles": True,
        "structured_data_present": True,
        "local_business_schema": True,
        "structured_data_matches_visible_content": True,
    }
    result = AIDiscoverabilityScorer().score(signals)
    assert result.score == 100
    assert result.confidence == 1.0
    assert result.blockers == ()


def test_noindex_caps_readiness() -> None:
    result = AIDiscoverabilityScorer().score(
        {
            "public_http_ok": True,
            "indexable": False,
            "important_content_textual": True,
            "services_clearly_described": True,
        }
    )
    assert result.score <= 25
    assert "indexable" in result.blockers


def test_sparse_positive_data_has_high_score_but_low_confidence() -> None:
    result = AIDiscoverabilityScorer().score(
        {"services_clearly_described": True}
    )
    assert result.score == 100
    assert result.confidence < 0.2


def test_invalid_site_signal_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        AIDiscoverabilityScorer().score({"indexable": "yes"})
