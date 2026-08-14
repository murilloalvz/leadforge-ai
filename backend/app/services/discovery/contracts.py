from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class DiscoveryQuery:
    niche: str
    city: str
    state: str
    limit: int = 10


@dataclass(frozen=True)
class DiscoveredBusiness:
    external_id: str
    name: str
    category: str | None
    city: str
    state: str
    website: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    source_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class DiscoveryProvider(Protocol):
    name: str

    def discover(self, query: DiscoveryQuery) -> tuple[DiscoveredBusiness, ...]: ...
