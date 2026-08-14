from urllib.parse import parse_qs

import httpx
import pytest

from app.services.discovery.contracts import DiscoveryQuery
from app.services.discovery.providers import DiscoveryProviderError, OpenStreetMapOverpassProvider


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
