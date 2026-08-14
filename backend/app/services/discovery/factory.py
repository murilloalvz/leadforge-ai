from app.core.config import get_settings
from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryProvider
from app.services.discovery.providers import (
    GooglePlacesProvider,
    MockDiscoveryProvider,
    OpenStreetMapOverpassProvider,
)

MOCK_BUSINESSES = (
    DiscoveredBusiness(
        external_id="mock/aurora",
        name="Clínica Aurora Demo",
        category="beauty",
        city="Campinas",
        state="SP",
        website="https://example.com",
        phone="+55 19 3000-0001",
        whatsapp="+55 19 99000-0001",
        source_url="https://example.com/mock/aurora",
        raw={"fictional": True},
    ),
    DiscoveredBusiness(
        external_id="mock/viva",
        name="Estética Viva Demo",
        category="beauty",
        city="Campinas",
        state="SP",
        phone="+55 19 3000-0002",
        source_url="https://example.com/mock/viva",
        raw={"fictional": True},
    ),
)


def _google_places_provider() -> GooglePlacesProvider:
    settings = get_settings()
    return GooglePlacesProvider(
        api_key=settings.google_places_api_key,
        endpoint=settings.google_places_endpoint,
        timeout_seconds=settings.google_places_timeout_seconds,
    )


def _overpass_provider() -> OpenStreetMapOverpassProvider:
    settings = get_settings()
    return OpenStreetMapOverpassProvider(
        endpoint=settings.overpass_endpoint,
        timeout_seconds=settings.overpass_timeout_seconds,
    )


def build_discovery_provider(name: str) -> DiscoveryProvider:
    if name == "auto":
        settings = get_settings()
        return _google_places_provider() if settings.google_places_api_key else _overpass_provider()
    if name == "google_places":
        return _google_places_provider()
    if name == "openstreetmap":
        return _overpass_provider()
    if name == "mock":
        return MockDiscoveryProvider(MOCK_BUSINESSES)
    raise ValueError(f"Provider de discovery não suportado: {name}")
