from app.services.opportunity import FindingCertainty, OpportunityContext
from app.services.opportunity.web_development import WebDevelopmentOpportunityModule


def test_web_opportunity_scores_only_observed_gaps() -> None:
    module = WebDevelopmentOpportunityModule()
    result = module.assess(
        OpportunityContext(
            signals={
                "public_http_ok": True,
                "indexable": True,
                "important_content_textual": True,
                "business_identity_clear": True,
                "services_clearly_described": False,
                "location_clearly_described": False,
                "descriptive_titles": True,
                "structured_data_present": False,
                "local_business_schema": False,
            },
            evidence={"page_title": "Clínica Exemplo"},
        )
    )

    assert result.service_category == "web_development"
    assert result.version == "web-development-v1"
    assert result.score == 40
    assert result.confidence == 1.0
    assert result.recommended_service == "Melhoria de site institucional"
    confirmed = [
        finding for finding in result.findings if finding.certainty is FindingCertainty.CONFIRMED
    ]
    assert {finding.key for finding in confirmed} == {
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
    assert result.confidence == 0.26
    assert unknown
    assert not any(
        finding.certainty is FindingCertainty.CONFIRMED for finding in result.findings
    )
