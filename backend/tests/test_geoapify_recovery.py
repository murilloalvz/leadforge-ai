import httpx

from app.services.discovery.contracts import DiscoveryQuery
from app.services.discovery.geoapify_recovery import RecoveringGeoapifyProvider


def test_sparse_dentist_results_recover_from_parent_healthcare_category() -> None:
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
            return httpx.Response(200, request=request, json={"results": []})

        if request.url.path.endswith("/places"):
            if params["categories"] == "healthcare.dentist":
                return httpx.Response(200, request=request, json={"features": []})

            assert params["categories"] == "healthcare"
            assert params["filter"] == "place:city-jundiai"
            return httpx.Response(
                200,
                request=request,
                json={
                    "features": [
                        {
                            "properties": {
                                "place_id": "odonto-1",
                                "name": "Odonto Jundiaí",
                                "city": "Jundiaí",
                                "state_code": "SP",
                                "formatted": "Rua A, Jundiaí - SP",
                                "categories": ["healthcare"],
                            }
                        },
                        {
                            "properties": {
                                "place_id": "hospital-1",
                                "name": "Hospital Central",
                                "city": "Jundiaí",
                                "state_code": "SP",
                                "formatted": "Rua B, Jundiaí - SP",
                                "categories": ["healthcare.hospital"],
                            }
                        },
                        {
                            "properties": {
                                "place_id": "wrong-city",
                                "name": "Odonto Campinas",
                                "city": "Campinas",
                                "state_code": "SP",
                                "formatted": "Rua C, Campinas - SP",
                                "categories": ["healthcare"],
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
                            "website": "https://odonto.example",
                            "contact": {"phone": "+55 11 3000-0000"},
                        }
                    }
                ]
            },
        )

    provider = RecoveringGeoapifyProvider(
        api_key="test-key",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    businesses = provider.discover(
        DiscoveryQuery(niche="dentistas", city="Jundiaí", state="SP", limit=2)
    )

    assert [business.name for business in businesses] == ["Odonto Jundiaí"]
    assert detail_calls == ["odonto-1"]
    assert businesses[0].raw["discovery_mode"] == "places_parent_category_recovery"
