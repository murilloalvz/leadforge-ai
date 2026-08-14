from app.core.config import get_settings
from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryProvider
from app.services.discovery.providers import (
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


def build_discovery_provider(name: str) -> DiscoveryProvider:
    if name == "openstreetmap":
        settings = get_settings()
        return OpenStreetMapOverpassProvider(
            endpoint=settings.overpass_endpoint,
            timeout_seconds=settings.overpass_timeout_seconds,
        )
    if name == "mock":
        return MockDiscoveryProvider(MOCK_BUSINESSES)
    raise ValueError(f"Provider de discovery não suportado: {name}")
