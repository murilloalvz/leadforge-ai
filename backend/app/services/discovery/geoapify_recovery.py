from __future__ import annotations

from typing import Any

from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryQuery
from app.services.discovery.geoapify_relevance import (
    RelevantGeoapifyProvider,
    _categories_from,
    _dedupe_candidates,
    _looks_like_street_name,
    _matches_categories,
    _name_matches_niche,
    _normalize,
    categories_for_niche,
)
from app.services.discovery.providers import DiscoveryProviderError


def recovery_categories_for_niche(niche: str) -> tuple[str, ...] | None:
    """Return a broader Places category only where a safe recovery rule is known."""
    normalized = _normalize(niche)
    if any(term in normalized for term in ("dentista", "odontologia", "odontologica")):
        return ("healthcare",)
    return None


class RecoveringGeoapifyProvider(RelevantGeoapifyProvider):
    """Fill sparse mapped results from broader Places categories inside the same city boundary."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.last_recovery_diagnostics: list[dict[str, object]] = []

    def _recovery_candidates(
        self,
        query: DiscoveryQuery,
        requested_categories: tuple[str, ...],
        recovery_categories: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        city_place_id = self._city_place_id(query)
        search_limit = min(max(query.limit * 6, query.limit), 40)
        payload = self._get_json(
            self.places_endpoint,
            {
                "categories": ",".join(recovery_categories),
                "filter": f"place:{city_place_id}",
                "lang": "pt",
                "limit": search_limit,
                "apiKey": self.api_key,
            },
            operation="places-recovery-search",
        )
        features = payload.get("features")
        if not isinstance(features, list):
            raise DiscoveryProviderError(
                "Resposta inesperada do Geoapify em places-recovery-search"
            )

        self.last_recovery_diagnostics = []
        candidates: list[dict[str, Any]] = []
        for feature in features:
            if not isinstance(feature, dict):
                continue
            properties = feature.get("properties")
            if not isinstance(properties, dict):
                continue

            place_id = properties.get("place_id")
            name = properties.get("name")
            categories = _categories_from(properties.get("categories"))
            city = properties.get("city")
            state_code = properties.get("state_code")
            specific_category = _matches_categories(categories, requested_categories)
            niche_name = isinstance(name, str) and _name_matches_niche(name, query.niche)

            rejection_reason: str | None = None
            if not isinstance(place_id, str):
                rejection_reason = "missing_place_id"
            elif not isinstance(name, str) or not name.strip():
                rejection_reason = "missing_business_name"
            elif _looks_like_street_name(name):
                rejection_reason = "street_like_name"
            elif isinstance(city, str) and _normalize(city) != _normalize(query.city):
                rejection_reason = "wrong_city"
            elif isinstance(state_code, str) and state_code.upper() != query.state.upper():
                rejection_reason = "wrong_state"
            elif not specific_category and not niche_name:
                rejection_reason = "no_dentist_signal"

            if len(self.last_recovery_diagnostics) < 20:
                self.last_recovery_diagnostics.append(
                    {
                        "name": name if isinstance(name, str) else None,
                        "categories": list(categories),
                        "city": city if isinstance(city, str) else None,
                        "state": state_code if isinstance(state_code, str) else None,
                        "specific_category_match": specific_category,
                        "niche_name_match": niche_name,
                        "accepted": rejection_reason is None,
                        "rejection_reason": rejection_reason,
                    }
                )

            if rejection_reason is not None:
                continue

            formatted = properties.get("formatted")
            candidates.append(
                {
                    "place_id": place_id,
                    "name": name.strip(),
                    "categories": categories,
                    "formatted": formatted if isinstance(formatted, str) else None,
                    "city": city,
                    "state_code": state_code,
                    "website": properties.get("website"),
                    "contact": properties.get("contact"),
                    "discovery_mode": "places_parent_category_recovery",
                }
            )

        return _dedupe_candidates(candidates)

    def discover(self, query: DiscoveryQuery) -> tuple[DiscoveredBusiness, ...]:
        self.last_recovery_diagnostics = []
        primary = list(super().discover(query))
        if len(primary) >= query.limit:
            return tuple(primary[: query.limit])

        requested_categories = categories_for_niche(query.niche)
        recovery_categories = recovery_categories_for_niche(query.niche)
        if not requested_categories or not recovery_categories:
            return tuple(primary[: query.limit])

        recovered_candidates = self._recovery_candidates(
            query,
            requested_categories,
            recovery_categories,
        )
        seen_external_ids = {business.external_id for business in primary}
        seen_names = {_normalize(business.name) for business in primary}
        for candidate in recovered_candidates:
            if len(primary) >= query.limit:
                break
            external_id = f"geoapify/{candidate['place_id']}"
            normalized_name = _normalize(str(candidate["name"]))
            if external_id in seen_external_ids or normalized_name in seen_names:
                continue
            business = self._to_business(query, candidate)
            primary.append(business)
            seen_external_ids.add(business.external_id)
            seen_names.add(normalized_name)

        return tuple(primary[: query.limit])
