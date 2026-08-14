from app.services.opportunity import FindingCertainty, OpportunityContext
from app.services.opportunity.web_development import WebDevelopmentOpportunityModule


def test_web_opportunity_scores_only_observed_gaps() -> None:
    module = WebDevelopmentOpportunityModule()
    result = module.assess(
        OpportunityContext(
            signals={
                "public_http_ok": True,
                "https_enabled": True,
                "mobile_viewport_present": False,
                "lead_capture_path_present": False,
                "action_cta_present": False,
                "important_content_textual": True,
                "business_identity_clear": True,
                "services_clearly_described": False,
                "location_clearly_described": False,
                "descriptive_titles": True,
                "meta_description_present": True,
                "canonical_present": True,
                "heading_structure_basic": True,
                "images_alt_attributes_complete": True,
                "structured_data_present": False,
                "local_business_schema": False,
                "indexable": True,
            },
            evidence={"page_title": "Clínica Exemplo"},
        )
    )

    assert result.service_category == "web_development"
    assert result.version == "web-development-v2"
    assert result.score == 43
    assert result.confidence == 1.0
    assert result.recommended_service == "Melhoria de site institucional"
    confirmed = [
        finding for finding in result.findings if finding.certainty is FindingCertainty.CONFIRMED
    ]
    assert {finding.key for finding in confirmed} == {
        "mobile_viewport_present",
        "lead_capture_path_present",
        "action_cta_present",
        "services_clearly_described",
        "location_clearly_described",
        "structured_data_present",
        "local_business_schema",
    }


def test_unknown_signal_does_not_become_confirmed_problem() -> None:
    module = WebDevelopmentOpportunityModule()
    result = module.assess(
        OpportunityContext(
            signals={"public_http_ok": True, "indexable": True},
            evidence={},
        )
    )

    unknown = [
        finding for finding in result.findings if finding.certainty is FindingCertainty.UNKNOWN
    ]
    assert result.score == 0
    assert result.confidence == 0.17
    assert unknown
    assert not any(
        finding.certainty is FindingCertainty.CONFIRMED for finding in result.findings
    )


def test_missing_form_is_not_a_problem_when_contact_path_exists() -> None:
    module = WebDevelopmentOpportunityModule()
    result = module.assess(
        OpportunityContext(
            signals={
                "public_http_ok": True,
                "https_enabled": True,
                "lead_capture_path_present": True,
                "action_cta_present": True,
                "form_present": False,
                "whatsapp_link_present": True,
            },
            evidence={"form_count": 0},
        )
    )

    assert not any(finding.key == "form_present" for finding in result.findings)
