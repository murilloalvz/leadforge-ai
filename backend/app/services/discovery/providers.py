from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

import httpx

from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryQuery


class DiscoveryProviderError(RuntimeError):
    """Raised when a discovery source cannot complete a query."""


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    plain = "".join(char for char in decomposed if not unicodedata.combining(char))
    return plain.casefold().strip()


def _escape_overpass_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _generic_name_regex(niche: str) -> str:
    ignored = {"para", "com", "uma", "uns", "das", "dos", "de", "da", "do", "e"}
    tokens = [
        token
        for token in re.findall(r"[a-z0-9]+", _normalize(niche))
        if len(token) >= 4 and token not in ignored
    ]
    if not tokens:
        raise ValueError("O nicho precisa ter ao menos uma palavra relevante")
    return "|".join(re.escape(token) for token in tokens[:4])


def _query_body(query: DiscoveryQuery) -> str:
    city = _escape_overpass_literal(query.city)
    normalized_niche = _normalize(query.niche)
    if any(term in normalized_niche for term in ("estetica", "aesthetic", "beauty")):
        selectors = [
            'nwr["shop"="beauty"](area.searchArea);',
            'nwr["name"~"est[eé]tica|aesthetic|beauty",i](area.searchArea);',
        ]
    else:
        pattern = _escape_overpass_literal(_generic_name_regex(query.niche))
        selectors = [f'nwr["name"~"{pattern}",i](area.searchArea);']

    joined = "\n  ".join(selectors)
    output_limit = min(max(query.limit * 4, query.limit), 100)
    return (
        "[out:json][timeout:15];\n"
        f'rel["name"="{city}"]["boundary"="administrative"]'
        '["admin_level"="8"]->.city;\n'
        ".city map_to_area -> .searchArea;\n"
        "(\n"
        f"  {joined}\n"
        ");\n"
        f"out center tags {output_limit};"
    )


def _first(tags: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = tags.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _state(tags: dict[str, Any], fallback: str) -> str:
    value = _first(tags, "addr:state")
    if value and len(value.strip()) == 2:
        return value.strip().upper()
    return fallback.upper()


def _category(tags: dict[str, Any]) -> str | None:
    values = [
        _first(tags, "shop"),
        _first(tags, "healthcare"),
        _first(tags, "amenity"),
        _first(tags, "beauty"),
    ]
    compact = [value for value in values if value]
    return ", ".join(compact) or None


def _public_payload(
    element_type: str,
    element_id: str,
    tags: dict[str, Any],
) -> dict[str, Any]:
    allowed = {
        "name",
        "brand",
        "operator",
        "shop",
        "beauty",
        "healthcare",
        "amenity",
        "website",
        "contact:website",
        "url",
        "phone",
        "contact:phone",
        "whatsapp",
        "contact:whatsapp",
        "addr:city",
        "addr:state",
    }
    selected_tags = {key: value for key, value in tags.items() if key in allowed}
    return {
        "element_type": element_type,
        "element_id": element_id,
        "tags": selected_tags,
    }


@dataclass
class MockDiscoveryProvider:
    businesses: tuple[DiscoveredBusiness, ...]
    name: str = "mock"

    def discover(self, query: DiscoveryQuery) -> tuple[DiscoveredBusiness, ...]:
        matches = [
            business
            for business in self.businesses
            if _normalize(business.city) == _normalize(query.city)
            and business.state.upper() == query.state.upper()
        ]
        return tuple(matches[: query.limit])


class GooglePlacesProvider:
    """Google Places Text Search provider with an explicit minimal field mask."""

    name = "google_places"
    field_mask = (
        "places.id,places.displayName,places.formattedAddress,places.primaryType,"
        "places.websiteUri,places.nationalPhoneNumber,places.googleMapsUri"
    )

    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://places.googleapis.com/v1/places:searchText",
        *,
        timeout_seconds: float = 12.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("LEADFORGE_GOOGLE_PLACES_API_KEY não configurada")
        self.api_key = api_key
        self.endpoint = endpoint
        self.client = client or httpx.Client(timeout=timeout_seconds, trust_env=False)

    def discover(self, query: DiscoveryQuery) -> tuple[DiscoveredBusiness, ...]:
        payload = {
            "textQuery": f"{query.niche} em {query.city}, {query.state}, Brasil",
            "pageSize": min(query.limit, 20),
            "languageCode": "pt-BR",
            "regionCode": "BR",
        }
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": self.field_mask,
        }
        try:
            response = self.client.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException as exc:
            raise DiscoveryProviderError("Google Places excedeu o tempo limite") from exc
        except httpx.HTTPStatusError as exc:
            raise DiscoveryProviderError(
                f"Google Places respondeu HTTP {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise DiscoveryProviderError("Falha de rede ao consultar Google Places") from exc
        except ValueError as exc:
            raise DiscoveryProviderError("Resposta inválida do Google Places") from exc

        places = data.get("places")
        if not isinstance(places, list):
            raise DiscoveryProviderError("Resposta inesperada do Google Places")

        businesses: list[DiscoveredBusiness] = []
        for place in places:
            if not isinstance(place, dict):
                continue
            place_id = place.get("id")
            display_name = place.get("displayName")
            name = display_name.get("text") if isinstance(display_name, dict) else None
            if not isinstance(place_id, str) or not isinstance(name, str) or not name.strip():
                continue

            source_url = place.get("googleMapsUri")
            businesses.append(
                DiscoveredBusiness(
                    external_id=f"google/{place_id}",
                    name=name.strip(),
                    category=(
                        place.get("primaryType")
                        if isinstance(place.get("primaryType"), str)
                        else None
                    ),
                    city=query.city,
                    state=query.state.upper(),
                    website=(
                        place.get("websiteUri")
                        if isinstance(place.get("websiteUri"), str)
                        else None
                    ),
                    phone=(
                        place.get("nationalPhoneNumber")
                        if isinstance(place.get("nationalPhoneNumber"), str)
                        else None
                    ),
                    source_url=source_url if isinstance(source_url, str) else None,
                    raw={
                        "place_id": place_id,
                        "formatted_address": place.get("formattedAddress"),
                        "primary_type": place.get("primaryType"),
                    },
                )
            )
            if len(businesses) >= query.limit:
                break

        return tuple(businesses)


class OpenStreetMapOverpassProvider:
    """Small interactive OSM discovery provider, not a bulk data harvester."""

    name = "openstreetmap"

    def __init__(
        self,
        endpoint: str = "https://overpass-api.de/api/interpreter",
        *,
        timeout_seconds: float = 25.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.client = client or httpx.Client(
            timeout=timeout_seconds,
            headers={
                "User-Agent": (
                    "LeadForgeAI/0.3 "
                    "(https://github.com/murilloalvz/leadforge-ai)"
                )
            },
        )

    def discover(self, query: DiscoveryQuery) -> tuple[DiscoveredBusiness, ...]:
        overpass_query = _query_body(query)
        try:
            response = self.client.post(self.endpoint, data={"data": overpass_query})
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException as exc:
            raise DiscoveryProviderError(
                "Fonte OpenStreetMap excedeu o tempo limite"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise DiscoveryProviderError(
                f"Fonte OpenStreetMap respondeu HTTP {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise DiscoveryProviderError(
                "Falha de rede ao consultar a fonte OpenStreetMap"
            ) from exc
        except ValueError as exc:
            raise DiscoveryProviderError("Resposta inválida da fonte OpenStreetMap") from exc

        elements = payload.get("elements")
        if not isinstance(elements, list):
            raise DiscoveryProviderError("Resposta inesperada da fonte OpenStreetMap")

        businesses: list[DiscoveredBusiness] = []
        seen: set[str] = set()
        for element in elements:
            if not isinstance(element, dict):
                continue
            tags = element.get("tags")
            if not isinstance(tags, dict):
                continue
            name = _first(tags, "name", "brand", "operator")
            if not name:
                continue

            element_type = str(element.get("type", "element"))
            element_id = str(element.get("id", ""))
            external_id = f"{element_type}/{element_id}"
            if external_id in seen:
                continue
            seen.add(external_id)

            website = _first(tags, "website", "contact:website", "url")
            phone = _first(tags, "contact:phone", "phone")
            whatsapp = _first(tags, "contact:whatsapp", "whatsapp")
            source_url = (
                f"https://www.openstreetmap.org/{element_type}/{element_id}"
                if element_id
                else None
            )
            businesses.append(
                DiscoveredBusiness(
                    external_id=external_id,
                    name=name,
                    category=_category(tags),
                    city=_first(tags, "addr:city") or query.city,
                    state=_state(tags, query.state),
                    website=website,
                    phone=phone,
                    whatsapp=whatsapp,
                    source_url=source_url,
                    raw=_public_payload(element_type, element_id, tags),
                )
            )
            if len(businesses) >= query.limit:
                break

        return tuple(businesses)
