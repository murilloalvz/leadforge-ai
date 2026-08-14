import pytest

from app.services.scoring.engine import OpportunityScorer


def complete_positive_signals() -> dict[str, bool]:
    return {
        "whatsapp_present": True,
        "website_present": True,
        "contact_form_present": True,
        "multiple_services": True,
        "booking_system_checked": True,
        "booking_system_present": False,
        "chat_automation_checked": True,
        "chat_automation_present": False,
        "strong_demand_signal": True,
        "active_social_presence": True,
        "medium_high_ticket_vertical": True,
        "multiple_contact_channels": True,
        "large_enterprise": False,
        "advanced_visible_automation": False,
        "possibly_inactive": False,
    }


def test_maximum_positive_profile_can_reach_100() -> None:
    result = OpportunityScorer().score(complete_positive_signals())
    assert result.total == 100
    assert result.confidence == 1.0
    assert result.version == "automation-v1.1"


def test_absence_is_not_assumed_without_check() -> None:
    result = OpportunityScorer().score({"booking_system_present": False})
    assert not any(
        component.signal == "no_visible_booking_system"
        for component in result.components
    )


def test_visible_advanced_automation_reduces_score() -> None:
    base = {
        "whatsapp_present": True,
        "website_present": True,
        "strong_demand_signal": True,
    }
    plain = OpportunityScorer().score(base)
    automated = OpportunityScorer().score(
        {**base, "advanced_visible_automation": True}
    )
    assert automated.total < plain.total


def test_missing_evidence_lowers_confidence() -> None:
    sparse = OpportunityScorer().score({"whatsapp_present": True})
    rich = OpportunityScorer().score(
        {
            key: False
            for key in (
                "whatsapp_present",
                "website_present",
                "contact_form_present",
                "multiple_services",
                "booking_system_checked",
                "chat_automation_checked",
                "strong_demand_signal",
                "active_social_presence",
                "medium_high_ticket_vertical",
                "multiple_contact_channels",
                "large_enterprise",
                "advanced_visible_automation",
                "possibly_inactive",
            )
        }
    )
    assert sparse.confidence < rich.confidence


def test_unchecked_presence_value_does_not_inflate_confidence() -> None:
    orphan_value = OpportunityScorer().score(
        {
            "booking_system_checked": False,
            "booking_system_present": False,
        }
    )
    checked_only = OpportunityScorer().score({"booking_system_checked": False})
    assert orphan_value.confidence == checked_only.confidence


def test_invalid_signal_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        OpportunityScorer().score({"whatsapp_present": "yes"})
