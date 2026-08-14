from app.core.config import get_settings
from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryProvider
from app.services.discovery.providers import (
    GeoapifyProvider,
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


def _geoapify_provider() -> GeoapifyProvider:
    settings = get_settings()
    return GeoapifyProvider(
        api_key=settings.geoapify_api_key,
        search_endpoint=settings.geoapify_search_endpoint,
        details_endpoint=settings.geoapify_details_endpoint,
        timeout_seconds=settings.geoapify_timeout_seconds,
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
        return _geoapify_provider() if settings.geoapify_api_key else _overpass_provider()
    if name == "geoapify":
        return _geoapify_provider()
    if name == "openstreetmap":
        return _overpass_provider()
    if name == "mock":
        return MockDiscoveryProvider(MOCK_BUSINESSES)
    raise ValueError(f"Provider de discovery não suportado: {name}")
