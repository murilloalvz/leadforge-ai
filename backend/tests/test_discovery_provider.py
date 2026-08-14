from urllib.parse import parse_qs

import httpx
import pytest

from app.services.discovery.contracts import DiscoveryQuery
from app.services.discovery.providers import (
    DiscoveryProviderError,
    GooglePlacesProvider,
    OpenStreetMapOverpassProvider,
)


def test_google_places_provider_uses_bounded_field_mask_and_maps_business() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-goog-api-key"] == "test-key"
        field_mask = request.headers["x-goog-fieldmask"]
        assert "places.websiteUri" in field_mask
        assert "places.nationalPhoneNumber" in field_mask
        assert "places.reviews" not in field_mask
        payload = request.read().decode()
        assert '"pageSize":5' in payload
        assert "clínicas de estética em Campinas, SP, Brasil" in payload
        return httpx.Response(
            200,
            request=request,
            json={
                "places": [
                    {
                        "id": "ChIJ123",
                        "displayName": {"text": "Clínica Exemplo"},
                        "formattedAddress": "Rua Exemplo, Campinas - SP, Brasil",
                        "primaryType": "beauty_salon",
                        "websiteUri": "https://clinic.example",
                        "nationalPhoneNumber": "(19) 3000-0000",
                        "googleMapsUri": "https://maps.google.com/?cid=123",
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = GooglePlacesProvider(api_key="test-key", client=client)
    businesses = provider.discover(
        DiscoveryQuery(niche="clínicas de estética", city="Campinas", state="SP", limit=5)
    )

    assert len(businesses) == 1
    business = businesses[0]
    assert business.external_id == "google/ChIJ123"
    assert business.name == "Clínica Exemplo"
    assert business.website == "https://clinic.example"
    assert business.phone == "(19) 3000-0000"
    assert business.category == "beauty_salon"
    assert business.source_url == "https://maps.google.com/?cid=123"
    assert business.raw == {
        "place_id": "ChIJ123",
        "formatted_address": "Rua Exemplo, Campinas - SP, Brasil",
        "primary_type": "beauty_salon",
    }


def test_google_places_provider_requires_api_key() -> None:
    with pytest.raises(ValueError, match="LEADFORGE_GOOGLE_PLACES_API_KEY"):
        GooglePlacesProvider(api_key="")


def test_google_places_provider_reports_safe_http_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = GooglePlacesProvider(api_key="test-key", client=client)

    with pytest.raises(DiscoveryProviderError, match="Google Places respondeu HTTP 429"):
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
