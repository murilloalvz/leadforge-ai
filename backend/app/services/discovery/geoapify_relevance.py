from __future__ import annotations

import re
import unicodedata
from collections import deque
from typing import Any

from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryQuery
from app.services.discovery.providers import DiscoveryProviderError, GeoapifyProvider


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    plain = "".join(char for char in decomposed if not unicodedata.combining(char))
    return plain.casefold().strip()


def categories_for_niche(niche: str) -> tuple[str, ...] | None:
    """Resolve only high-confidence niche aliases to Geoapify Places categories.

    Unknown niches intentionally return None. In that case the provider keeps the textual
    geocoding fallback instead of guessing a broad category and presenting noisy results as
    precise matches.
    """
    normalized = _normalize(niche)
    mappings = (
        (
            ("estetica", "aesthetic", "beauty clinic", "clinica de beleza"),
            ("commercial.health_and_beauty", "service.beauty.spa"),
        ),
        (("dentista", "odontologia", "odontologica"), ("healthcare.dentist",)),
        (("academia", "fitness", "gym"), ("sport.fitness.fitness_centre",)),
    )
    for aliases, categories in mappings:
        if any(alias in normalized for alias in aliases):
            return categories
    return None


def _categories_from(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _matches_categories(observed: tuple[str, ...], requested: tuple[str, ...]) -> bool:
    return any(
        actual == expected or actual.startswith(f"{expected}.")
        for actual in observed
        for expected in requested
    )


def _category_label(categories: tuple[str, ...]) -> str | None:
    return ";".join(categories[:3]) or None


def _brand_key(name: str) -> str:
    normalized = _normalize(name)
    normalized = re.sub(r"\s*[-–—:]\s*unidade\b.*$", "", normalized)
    normalized = re.sub(r"\bunidade\s+[a-z0-9]+.*$", "", normalized).strip(" -–—:")
    return normalized


def _diversify_by_brand(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Interleave brand groups without deleting legitimate branch locations."""
    groups: dict[str, deque[dict[str, Any]]] = {}
    order: list[str] = []
    for item in items:
        key = _brand_key(str(item["name"]))
        if key not in groups:
            groups[key] = deque()
            order.append(key)
        groups[key].append(item)

    diversified: list[dict[str, Any]] = []
    while groups:
        for key in tuple(order):
            group = groups.get(key)
            if not group:
                continue
            diversified.append(group.popleft())
            if not group:
                del groups[key]
        order = [key for key in order if key in groups]
    return diversified


class RelevantGeoapifyProvider(GeoapifyProvider):
    """Geoapify provider with category + city-boundary discovery for mapped niches."""

    name = "geoapify"

    def __init__(
        self,
        api_key: str,
        search_endpoint: str = "https://api.geoapify.com/v1/geocode/search",
        places_endpoint: str = "https://api.geoapify.com/v2/places",
        details_endpoint: str = "https://api.geoapify.com/v2/place-details",
        *,
        timeout_seconds: float = 12.0,
        client: Any = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            search_endpoint=search_endpoint,
            details_endpoint=details_endpoint,
            timeout_seconds=timeout_seconds,
            client=client,
        )
        self.places_endpoint = places_endpoint
        self._city_place_cache: dict[tuple[str, str], str] = {}

    def _city_place_id(self, query: DiscoveryQuery) -> str:
        cache_key = (_normalize(query.city), query.state.upper())
        cached = self._city_place_cache.get(cache_key)
        if cached:
            return cached

        payload = self._get_json(
            self.search_endpoint,
            {
                "text": f"{query.city}, {query.state}, Brasil",
                "type": "city",
                "filter": "countrycode:br",
                "lang": "pt",
                "limit": 5,
                "format": "json",
                "apiKey": self.api_key,
            },
            operation="city-geocode",
        )
        results = payload.get("results")
        if not isinstance(results, list):
            raise DiscoveryProviderError("Resposta inesperada do Geoapify em city-geocode")

        fallback: str | None = None
        for result in results:
            if not isinstance(result, dict) or result.get("result_type") != "city":
                continue
            place_id = result.get("place_id")
            if not isinstance(place_id, str) or not place_id:
                continue
            fallback = fallback or place_id
            city = result.get("city") or result.get("name")
            state_code = result.get("state_code")
            city_matches = isinstance(city, str) and _normalize(city) == _normalize(query.city)
            state_matches = (
                not isinstance(state_code, str) or state_code.upper() == query.state.upper()
            )
            if city_matches and state_matches:
                self._city_place_cache[cache_key] = place_id
                return place_id

        if fallback:
            self._city_place_cache[cache_key] = fallback
            return fallback
        raise DiscoveryProviderError("Geoapify não encontrou a boundary da cidade solicitada")

    def _places_candidates(
        self,
        query: DiscoveryQuery,
        requested_categories: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        city_place_id = self._city_place_id(query)
        search_limit = min(max(query.limit * 4, query.limit), 40)
        payload = self._get_json(
            self.places_endpoint,
            {
                "categories": ",".join(requested_categories),
                "filter": f"place:{city_place_id}",
                "lang": "pt",
                "limit": search_limit,
                "apiKey": self.api_key,
            },
            operation="places-search",
        )
        features = payload.get("features")
        if not isinstance(features, list):
            raise DiscoveryProviderError("Resposta inesperada do Geoapify em places-search")

        candidates: list[dict[str, Any]] = []
        seen_place_ids: set[str] = set()
        seen_name_address: set[tuple[str, str]] = set()
        for feature in features:
            if not isinstance(feature, dict):
                continue
            properties = feature.get("properties")
            if not isinstance(properties, dict):
                continue

            place_id = properties.get("place_id")
            name = properties.get("name") or properties.get("address_line1")
            categories = _categories_from(properties.get("categories"))
            if (
                not isinstance(place_id, str)
                or not isinstance(name, str)
                or not name.strip()
                or not _matches_categories(categories, requested_categories)
            ):
                continue
            if place_id in seen_place_ids:
                continue

            formatted = properties.get("formatted")
            address_key = _normalize(formatted) if isinstance(formatted, str) else ""
            exact_key = (_normalize(name), address_key)
            if address_key and exact_key in seen_name_address:
                continue

            seen_place_ids.add(place_id)
            if address_key:
                seen_name_address.add(exact_key)
            candidates.append(
                {
                    "place_id": place_id,
                    "name": name.strip(),
                    "categories": categories,
                    "formatted": formatted if isinstance(formatted, str) else None,
                    "city": properties.get("city"),
                    "state_code": properties.get("state_code"),
                    "website": properties.get("website"),
                    "contact": properties.get("contact"),
                }
            )

        return _diversify_by_brand(candidates)

    def _to_business(
        self,
        query: DiscoveryQuery,
        candidate: dict[str, Any],
    ) -> DiscoveredBusiness:
        place_id = str(candidate["place_id"])
        details = self._details(place_id)
        contact = details.get("contact")
        if not isinstance(contact, dict):
            contact = candidate.get("contact") if isinstance(candidate.get("contact"), dict) else {}
        phone = contact.get("phone") if isinstance(contact, dict) else None
        website = details.get("website") or candidate.get("website")
        categories = candidate["categories"]
        state_code = candidate.get("state_code")

        return DiscoveredBusiness(
            external_id=f"geoapify/{place_id}",
            name=str(candidate["name"]),
            category=_category_label(categories),
            city=candidate.get("city") if isinstance(candidate.get("city"), str) else query.city,
            state=(
                state_code.upper()
                if isinstance(state_code, str) and len(state_code) == 2
                else query.state.upper()
            ),
            website=website if isinstance(website, str) else None,
            phone=phone if isinstance(phone, str) else None,
            source_url="https://www.geoapify.com/places-api/",
            raw={
                "place_id": place_id,
                "formatted_address": candidate.get("formatted"),
                "categories": list(categories),
                "data_source": "openstreetmap",
                "discovery_mode": "places_category_boundary",
            },
        )

    def discover(self, query: DiscoveryQuery) -> tuple[DiscoveredBusiness, ...]:
        requested_categories = categories_for_niche(query.niche)
        if not requested_categories:
            return super().discover(query)

        candidates = self._places_candidates(query, requested_categories)
        return tuple(self._to_business(query, item) for item in candidates[: query.limit])
