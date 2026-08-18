from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryQuery
from scripts.validate_geoapify import summarize_query


def test_live_validation_summary_does_not_export_contact_values() -> None:
    query = DiscoveryQuery(niche="dentistas", city="Jundiaí", state="SP", limit=1)
    business = DiscoveredBusiness(
        external_id="geoapify/example",
        name="Clínica Exemplo",
        category="healthcare.dentist",
        city="Jundiaí",
        state="SP",
        website="https://example.test/private-path",
        phone="+55 11 99999-0000",
        raw={"discovery_mode": "places_parent_category_recovery"},
    )

    summary = summarize_query(query, (business,), latency_ms=123.456)
    exported = summary["businesses"][0]

    assert summary["website_count"] == 1
    assert summary["phone_count"] == 1
    assert summary["discovery_mode"] == "places_category_boundary_with_recovery"
    assert summary["estimated_api_requests"] == 3
    assert exported["website_present"] is True
    assert exported["phone_present"] is True
    assert exported["discovery_mode"] == "places_parent_category_recovery"
    assert "website" not in exported
    assert "phone" not in exported


def test_live_validation_estimates_sparse_recovery_requests() -> None:
    query = DiscoveryQuery(niche="dentistas", city="Jundiaí", state="SP", limit=4)

    summary = summarize_query(query, (), latency_ms=100.0)

    assert summary["estimated_api_requests"] == 4
    assert summary["discovery_mode"] == "places_category_boundary_with_recovery"
