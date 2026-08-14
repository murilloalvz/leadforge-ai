from urllib.parse import parse_qs

import httpx
import pytest

from app.services.discovery.contracts import DiscoveryQuery
from app.services.discovery.providers import (
    DiscoveryProviderError,
    GeoapifyProvider,
    OpenStreetMapOverpassProvider,
)


def test_geoapify_provider_searches_amenities_and_enriches_business() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        if request.url.path.endswith("/geocode/search"):
            assert params["apiKey"] == "test-key"
            assert params["text"] == "clínicas de estética, Campinas, SP, Brasil"
            assert params["type"] == "amenity"
            assert params["filter"] == "countrycode:br"
            assert params["limit"] == "5"
            return httpx.Response(
                200,
                request=request,
                json={
                    "results": [
                        {
                            "place_id": "geo-123",
                            "name": "Clínica Exemplo",
                            "city": "Campinas",
                            "formatted": "Rua Exemplo, Campinas - SP, Brasil",
                            "categories": ["commercial.health_and_beauty"],
                        }
                    ]
                },
            )
        assert request.url.path.endswith("/place-details")
        assert params["id"] == "geo-123"
        assert params["features"] == "details"
        return httpx.Response(
            200,
            request=request,
            json={
                "features": [
                    {
                        "properties": {
                            "feature_type": "details",
                            "website": "https://clinic.example",
                            "contact": {"phone": "+55 19 3000-0000"},
                        }
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = GeoapifyProvider(api_key="test-key", client=client)
    businesses = provider.discover(
        DiscoveryQuery(niche="clínicas de estética", city="Campinas", state="SP", limit=5)
    )

    assert len(businesses) == 1
    business = businesses[0]
    assert business.external_id == "geoapify/geo-123"
    assert business.name == "Clínica Exemplo"
    assert business.website == "https://clinic.example"
    assert business.phone == "+55 19 3000-0000"
    assert business.category == "commercial.health_and_beauty"
    assert business.raw == {
        "place_id": "geo-123",
        "formatted_address": "Rua Exemplo, Campinas - SP, Brasil",
        "categories": ["commercial.health_and_beauty"],
        "data_source": "openstreetmap",
    }


def test_geoapify_provider_requires_api_key() -> None:
    with pytest.raises(ValueError, match="LEADFORGE_GEOAPIFY_API_KEY"):
        GeoapifyProvider(api_key="")


def test_geoapify_provider_reports_safe_http_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = GeoapifyProvider(api_key="test-key", client=client)

    with pytest.raises(
        DiscoveryProviderError,
        match="Geoapify respondeu HTTP 429 em geocode-search",
    ):
        provider.discover(
            DiscoveryQuery(niche="barbearia", city="Campinas", state="SP", limit=5)
        )


def test_overpass_provider_builds_small_query_and_minimizes_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = parse_qs(request.content.decode())
        query = payload["data"][0]
        assert 'rel["name"="Campinas"]' in query
        assert '["admin_level"="8"]' in query
        assert ".city map_to_area -> .searchArea;" in query
        assert 'nwr["shop"="beauty"]' in query
        assert 'nwr["beauty"]' not in query
        assert "out center tags 20;" in query
        return httpx.Response(
            200,
            json={
                "elements": [
                    {
                        "type": "node",
                        "id": 123,
                        "tags": {
                            "name": "Clínica Exemplo",
                            "shop": "beauty",
                            "website": "https://clinic.example",
                            "contact:phone": "+55 19 3000-0000",
                            "contact:whatsapp": "+55 19 99000-0000",
                            "contact:email": "nao-deve-ser-persistido@example.com",
                            "addr:city": "Campinas",
                            "addr:state": "SP",
                        },
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenStreetMapOverpassProvider(client=client)
    businesses = provider.discover(
        DiscoveryQuery(niche="clínicas de estética", city="Campinas", state="SP", limit=5)
    )

    assert len(businesses) == 1
    business = businesses[0]
    assert business.name == "Clínica Exemplo"
    assert business.website == "https://clinic.example"
    assert business.whatsapp == "+55 19 99000-0000"
    assert business.source_url == "https://www.openstreetmap.org/node/123"
    assert "contact:email" not in business.raw["tags"]


def test_overpass_provider_reports_safe_http_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenStreetMapOverpassProvider(client=client)

    with pytest.raises(
        DiscoveryProviderError,
        match="Fonte OpenStreetMap respondeu HTTP 503",
    ):
        provider.discover(
            DiscoveryQuery(niche="barbearia", city="Campinas", state="SP", limit=5)
        )


def test_overpass_provider_reports_timeout_without_leaking_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("simulated timeout", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenStreetMapOverpassProvider(client=client)

    with pytest.raises(
        DiscoveryProviderError,
        match="Fonte OpenStreetMap excedeu o tempo limite",
    ):
        provider.discover(
            DiscoveryQuery(niche="barbearia", city="Campinas", state="SP", limit=5)
        )
