from app.services.scoring.engine import OpportunityScorer


def test_high_opportunity_profile_scores_high() -> None:
    signals = {
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
    result = OpportunityScorer().score(signals)
    assert result.total >= 75
    assert result.confidence >= 0.9
    assert any(c.signal == "no_visible_booking_system" for c in result.components)


def test_absence_is_not_assumed_without_check() -> None:
    result = OpportunityScorer().score({"booking_system_present": False})
    assert not any(c.signal == "no_visible_booking_system" for c in result.components)


def test_visible_advanced_automation_reduces_score() -> None:
    base = {"whatsapp_present": True, "website_present": True, "strong_demand_signal": True}
    plain = OpportunityScorer().score(base)
    automated = OpportunityScorer().score({**base, "advanced_visible_automation": True})
    assert automated.total < plain.total


def test_missing_evidence_lowers_confidence() -> None:
    sparse = OpportunityScorer().score({"whatsapp_present": True})
    rich = OpportunityScorer().score({key: False for key in [
        "whatsapp_present", "website_present", "contact_form_present", "multiple_services",
        "booking_system_checked", "booking_system_present", "chat_automation_checked",
        "chat_automation_present", "strong_demand_signal", "active_social_presence",
        "medium_high_ticket_vertical", "multiple_contact_channels", "large_enterprise",
        "advanced_visible_automation", "possibly_inactive"
    ]})
    assert sparse.confidence < rich.confidence
