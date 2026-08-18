from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from app.services.discovery.contracts import DiscoveredBusiness, DiscoveryQuery
from app.services.discovery.geoapify_relevance import (
    RelevantGeoapifyProvider,
    categories_for_niche,
)
from app.services.discovery.providers import DiscoveryProviderError

DEFAULT_QUERIES = (
    DiscoveryQuery(niche="clínicas de estética", city="Campinas", state="SP", limit=4),
    DiscoveryQuery(niche="dentistas", city="Jundiaí", state="SP", limit=4),
    DiscoveryQuery(niche="academias", city="Sorocaba", state="SP", limit=4),
)


def summarize_query(
    query: DiscoveryQuery,
    businesses: tuple[DiscoveredBusiness, ...],
    latency_ms: float,
) -> dict[str, object]:
    categorized = categories_for_niche(query.niche) is not None
    return {
        "query": {
            "niche": query.niche,
            "city": query.city,
            "state": query.state,
            "limit": query.limit,
        },
        "discovery_mode": "places_category_boundary" if categorized else "textual_fallback",
        "latency_ms": round(latency_ms, 1),
        "business_count": len(businesses),
        "website_count": sum(bool(item.website) for item in businesses),
        "phone_count": sum(bool(item.phone) for item in businesses),
        "estimated_api_requests": len(businesses) + (2 if categorized else 1),
        "businesses": [
            {
                "external_id": item.external_id,
                "name": item.name,
                "category": item.category,
                "website_present": bool(item.website),
                "phone_present": bool(item.phone),
            }
            for item in businesses
        ],
    }


def main() -> int:
    api_key = os.getenv("LEADFORGE_GEOAPIFY_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "LEADFORGE_GEOAPIFY_API_KEY não configurada; use um segredo fora do repositório."
        )

    timeout_seconds = float(os.getenv("LEADFORGE_GEOAPIFY_TIMEOUT_SECONDS", "12"))
    output_path = Path(
        os.getenv(
            "LEADFORGE_GEOAPIFY_REPORT_PATH",
            "artifacts/geoapify-live-validation.json",
        )
    )
    provider = RelevantGeoapifyProvider(api_key=api_key, timeout_seconds=timeout_seconds)

    query_results: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []
    for query in DEFAULT_QUERIES:
        started_at = perf_counter()
        try:
            businesses = provider.discover(query)
        except DiscoveryProviderError as exc:
            failures.append(
                {
                    "niche": query.niche,
                    "city": query.city,
                    "state": query.state,
                    "error": str(exc),
                }
            )
            continue

        latency_ms = (perf_counter() - started_at) * 1000
        query_results.append(summarize_query(query, businesses, latency_ms))

    total_businesses = sum(int(result["business_count"]) for result in query_results)
    website_count = sum(int(result["website_count"]) for result in query_results)
    phone_count = sum(int(result["phone_count"]) for result in query_results)
    latencies = [float(result["latency_ms"]) for result in query_results]
    estimated_api_requests = sum(
        int(result["estimated_api_requests"]) for result in query_results
    )

    report = {
        "schema_version": "geoapify-live-validation-v2",
        "generated_at": datetime.now(UTC).isoformat(),
        "provider": "geoapify",
        "sample_query_count": len(DEFAULT_QUERIES),
        "successful_query_count": len(query_results),
        "failed_query_count": len(failures),
        "total_businesses": total_businesses,
        "website_coverage": round(website_count / total_businesses, 3)
        if total_businesses
        else 0.0,
        "phone_coverage": round(phone_count / total_businesses, 3)
        if total_businesses
        else 0.0,
        "average_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else None,
        "max_latency_ms": max(latencies) if latencies else None,
        "estimated_api_requests": estimated_api_requests,
        "provider_health_passed": not failures and total_businesses > 0,
        "queries": query_results,
        "failures": failures,
        "note": (
            "Small-sample provider health, relevance and coverage check; this is not proof of "
            "production recall, accuracy or SLA reliability."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["provider_health_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
