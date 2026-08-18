import httpx

from app.services.discovery.contracts import DiscoveryQuery
from app.services.discovery.geoapify_relevance import (
    RelevantGeoapifyProvider,
    categories_for_niche,
)


def test_categories_for_niche_only_maps_high_confidence_aliases() -> None:
    assert categories_for_niche("clínicas de estética") == (
        "commercial.health_and_beauty",
        "service.beauty.spa",
    )
    assert categories_for_niche("dentistas") == ("healthcare.dentist",)
    assert categories_for_niche("academias") == ("sport.fitness.fitness_centre",)
    assert categories_for_niche("consultoria empresarial") is None


def test_relevant_geoapify_uses_city_boundary_filters_noise_and_diversifies_brands() -> None:
    detail_calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        if request.url.path.endswith("/geocode/search"):
            assert params["text"] == "Sorocaba, SP, Brasil"
            assert params["type"] == "city"
            assert params["filter"] == "countrycode:br"
            return httpx.Response(
                200,
                request=request,
                json={
                    "results": [
                        {
                            "place_id": "city-sorocaba",
                            "name": "Sorocaba",
                            "city": "Sorocaba",
                            "state_code": "SP",
                            "result_type": "city",
                        }
                    ]
                },
            )
        if request.url.path.endswith("/places"):
            assert params["categories"] == "sport.fitness.fitness_centre"
            assert params["filter"] == "place:city-sorocaba"
            assert params["limit"] == "12"
            return httpx.Response(
                200,
                request=request,
                json={
                    "features": [
                        {
                            "properties": {
                                "place_id": "g1",
                                "name": "Ghimper Academias",
                                "formatted": "Rua A, Sorocaba - SP",
                                "city": "Sorocaba",
                                "state_code": "SP",
                                "categories": ["sport.fitness.fitness_centre"],
                            }
                        },
                        {
                            "properties": {
                                "place_id": "g2",
                                "name": "Ghimper Academias - Unidade Max",
                                "formatted": "Rua B, Sorocaba - SP",
                                "city": "Sorocaba",
                                "state_code": "SP",
                                "categories": ["sport.fitness.fitness_centre"],
                            }
                        },
                        {
                            "properties": {
                                "place_id": "s1",
                                "name": "Smart Fit Centro",
                                "formatted": "Rua C, Sorocaba - SP",
                                "city": "Sorocaba",
                                "state_code": "SP",
                                "categories": ["sport.fitness.fitness_centre"],
                            }
                        },
                        {
                            "properties": {
                                "place_id": "hospital",
                                "name": "Hospital Exemplo",
                                "formatted": "Rua D, Sorocaba - SP",
                                "city": "Sorocaba",
                                "state_code": "SP",
                                "categories": ["healthcare.hospital"],
                            }
                        },
                        {
                            "properties": {
                                "place_id": "g1-duplicate",
                                "name": "Ghimper Academias",
                                "formatted": "Rua A, Sorocaba - SP",
                                "city": "Sorocaba",
                                "state_code": "SP",
                                "categories": ["sport.fitness.fitness_centre"],
                            }
                        },
                    ]
                },
            )
        assert request.url.path.endswith("/place-details")
        detail_calls.append(params["id"])
        return httpx.Response(
            200,
            request=request,
            json={
                "features": [
                    {
                        "properties": {
                            "feature_type": "details",
                            "website": f"https://{params['id']}.example",
                            "contact": {"phone": "+55 15 3000-0000"},
                        }
                    }
                ]
            },
        )

    provider = RelevantGeoapifyProvider(
        api_key="test-key",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    businesses = provider.discover(
        DiscoveryQuery(niche="academias", city="Sorocaba", state="SP", limit=3)
    )

    assert [business.name for business in businesses] == [
        "Ghimper Academias",
        "Smart Fit Centro",
        "Ghimper Academias - Unidade Max",
    ]
    assert "Hospital Exemplo" not in {business.name for business in businesses}
    assert detail_calls == ["g1", "s1", "g2"]
    assert all(
        business.raw["discovery_mode"] == "places_category_boundary"
        for business in businesses
    )


def test_relevant_geoapify_keeps_textual_fallback_for_unmapped_niche() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        if request.url.path.endswith("/geocode/search"):
            assert params["text"] == "consultoria empresarial, Campinas, SP, Brasil"
            assert params["type"] == "amenity"
            return httpx.Response(
                200,
                request=request,
                json={
                    "results": [
                        {
                            "place_id": "consultoria-1",
                            "name": "Consultoria Exemplo",
                            "city": "Campinas",
                            "formatted": "Campinas - SP, Brasil",
                            "categories": ["office.company"],
                        }
                    ]
                },
            )
        assert request.url.path.endswith("/place-details")
        return httpx.Response(
            200,
            request=request,
            json={"features": [{"properties": {"feature_type": "details"}}]},
        )

    provider = RelevantGeoapifyProvider(
        api_key="test-key",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    businesses = provider.discover(
        DiscoveryQuery(
            niche="consultoria empresarial",
            city="Campinas",
            state="SP",
            limit=1,
        )
    )

    assert [business.name for business in businesses] == ["Consultoria Exemplo"]
    assert businesses[0].raw["data_source"] == "openstreetmap"
