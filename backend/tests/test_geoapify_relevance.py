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
            if params["type"] == "city":
                assert params["text"] == "Sorocaba, SP, Brasil"
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
            assert params["type"] == "amenity"
            return httpx.Response(200, request=request, json={"results": []})
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


def test_places_rejects_address_fallback_even_when_category_matches() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        if request.url.path.endswith("/geocode/search"):
            if params["type"] == "city":
                return httpx.Response(
                    200,
                    request=request,
                    json={
                        "results": [
                            {
                                "place_id": "city-campinas",
                                "name": "Campinas",
                                "city": "Campinas",
                                "state_code": "SP",
                                "result_type": "city",
                            }
                        ]
                    },
                )
            return httpx.Response(200, request=request, json={"results": []})
        if request.url.path.endswith("/places"):
            return httpx.Response(
                200,
                request=request,
                json={
                    "features": [
                        {
                            "properties": {
                                "place_id": "street-like",
                                "address_line1": "Rua José Bognoni",
                                "formatted": "Rua José Bognoni, Campinas - SP",
                                "city": "Campinas",
                                "state_code": "SP",
                                "categories": [
                                    "building",
                                    "commercial.health_and_beauty",
                                ],
                            }
                        },
                        {
                            "properties": {
                                "place_id": "real-beauty",
                                "name": "Estética Aurora",
                                "formatted": "Rua A, Campinas - SP",
                                "city": "Campinas",
                                "state_code": "SP",
                                "categories": ["commercial.health_and_beauty"],
                            }
                        },
                    ]
                },
            )
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
        DiscoveryQuery(niche="clínicas de estética", city="Campinas", state="SP", limit=1)
    )

    assert [business.name for business in businesses] == ["Estética Aurora"]


def test_sparse_mapped_niche_uses_validated_textual_fallback() -> None:
    detail_calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        if request.url.path.endswith("/geocode/search"):
            if params["type"] == "city":
                return httpx.Response(
                    200,
                    request=request,
                    json={
                        "results": [
                            {
                                "place_id": "city-jundiai",
                                "name": "Jundiaí",
                                "city": "Jundiaí",
                                "state_code": "SP",
                                "result_type": "city",
                            }
                        ]
                    },
                )
            assert params["text"] == "dentistas, Jundiaí, SP, Brasil"
            return httpx.Response(
                200,
                request=request,
                json={
                    "results": [
                        {
                            "place_id": "dent-1",
                            "name": "Odonto Jundiaí",
                            "city": "Jundiaí",
                            "state_code": "SP",
                            "formatted": "Rua A, Jundiaí - SP",
                            "categories": ["healthcare"],
                        },
                        {
                            "place_id": "hospital-1",
                            "name": "Hospital Central",
                            "city": "Jundiaí",
                            "state_code": "SP",
                            "formatted": "Rua B, Jundiaí - SP",
                            "categories": ["healthcare.hospital"],
                        },
                        {
                            "place_id": "wrong-city",
                            "name": "Odonto Campinas",
                            "city": "Campinas",
                            "state_code": "SP",
                            "formatted": "Rua C, Campinas - SP",
                            "categories": ["healthcare.dentist"],
                        },
                    ]
                },
            )
        if request.url.path.endswith("/places"):
            assert params["categories"] == "healthcare.dentist"
            return httpx.Response(200, request=request, json={"features": []})
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
                            "website": "https://odonto.example",
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
        DiscoveryQuery(niche="dentistas", city="Jundiaí", state="SP", limit=2)
    )

    assert [business.name for business in businesses] == ["Odonto Jundiaí"]
    assert detail_calls == ["dent-1"]
    assert businesses[0].raw["discovery_mode"] == "validated_textual_fallback"


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
