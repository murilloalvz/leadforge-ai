from __future__ import annotations

import csv
import io
import json
import tempfile
import time
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

QUERIES = (
    {
        "niche": "clínicas de estética",
        "city": "Campinas",
        "state": "SP",
        "provider": "openstreetmap",
        "limit": 6,
        "analyze_sites": True,
        "site_audit_limit": 3,
    },
    {
        "niche": "barbearia",
        "city": "Campinas",
        "state": "SP",
        "provider": "openstreetmap",
        "limit": 6,
        "analyze_sites": True,
        "site_audit_limit": 3,
    },
)


def _validate_exports(client: TestClient, run: dict[str, Any]) -> None:
    run_id = run["id"]
    json_response = client.get(f"/discovery-runs/{run_id}/export?format=json")
    if json_response.status_code != 200:
        raise RuntimeError(f"JSON export falhou para run {run_id}: {json_response.text}")
    exported = json_response.json()
    if exported["schema_version"] != "discovery-export-v1":
        raise RuntimeError(f"Schema inesperado no JSON export do run {run_id}")
    if len(exported["candidates"]) != len(run["candidates"]):
        raise RuntimeError(f"JSON export divergiu do run {run_id}")

    csv_response = client.get(f"/discovery-runs/{run_id}/export?format=csv")
    if csv_response.status_code != 200:
        raise RuntimeError(f"CSV export falhou para run {run_id}: {csv_response.text}")
    text = csv_response.content.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    if len(rows) != len(run["candidates"]):
        raise RuntimeError(f"CSV export divergiu do run {run_id}")


def _validate_run(run: dict[str, Any]) -> None:
    if run["status"] != "completed":
        raise RuntimeError(f"Run {run['id']} não concluiu: {run['status']}")

    ranks = [candidate["rank"] for candidate in run["candidates"]]
    expected = list(range(1, len(ranks) + 1))
    if ranks != expected:
        raise RuntimeError(f"Ranking inconsistente no run {run['id']}: {ranks}")

    prospect_ids = [candidate["prospect_id"] for candidate in run["candidates"]]
    if len(prospect_ids) != len(set(prospect_ids)):
        raise RuntimeError(f"Prospects duplicados no run {run['id']}")

    for candidate in run["candidates"]:
        if candidate["site_audit_id"] is not None and candidate["opportunity"] is None:
            raise RuntimeError(
                "Candidato auditado sem OpportunityAssessment: "
                f"run={run['id']} prospect={candidate['prospect_id']}"
            )


def _summary(run: dict[str, Any]) -> dict[str, Any]:
    with_website = sum(bool(candidate["website"]) for candidate in run["candidates"])
    with_opportunity = sum(candidate["opportunity"] is not None for candidate in run["candidates"])
    top = []
    for candidate in run["candidates"][:3]:
        opportunity = candidate["opportunity"]
        top.append(
            {
                "rank": candidate["rank"],
                "name": candidate["name"],
                "website": candidate["website"],
                "source_url": candidate["source_url"],
                "priority_bucket": candidate["priority_bucket"],
                "opportunity_score": opportunity["score"] if opportunity else None,
                "opportunity_confidence": opportunity["confidence"] if opportunity else None,
                "recommended_service": (
                    opportunity["recommended_service"] if opportunity else None
                ),
                "findings": (
                    [
                        {
                            "certainty": finding["certainty"],
                            "title": finding["title"],
                        }
                        for finding in opportunity["findings"]
                    ]
                    if opportunity
                    else []
                ),
            }
        )

    return {
        "run_id": run["id"],
        "niche": run["niche"],
        "city": run["city"],
        "discovered_count": run["discovered_count"],
        "candidate_count": len(run["candidates"]),
        "with_website": with_website,
        "audited_count": run["audited_count"],
        "audit_failure_count": run["audit_failure_count"],
        "with_opportunity": with_opportunity,
        "top_candidates": top,
    }


def main() -> int:
    reports: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="leadforge-validation-") as temp_dir:
        database_path = Path(temp_dir) / "validation.db"
        engine = create_engine(f"sqlite:///{database_path}")
        session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        Base.metadata.create_all(engine)

        def override_get_db():
            with session_factory() as db:
                yield db

        original_overrides = dict(app.dependency_overrides)
        app.dependency_overrides[get_db] = override_get_db
        try:
            client = TestClient(app)
            for index, query in enumerate(QUERIES):
                if index:
                    time.sleep(2)
                response = client.post("/discovery-runs", json=query)
                if response.status_code != 201:
                    raise RuntimeError(
                        f"Discovery falhou para {query['niche']}: "
                        f"status={response.status_code} body={response.text}"
                    )
                run = response.json()
                _validate_run(run)
                _validate_exports(client, run)
                reports.append(_summary(run))
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(original_overrides)
            engine.dispose()

    total_candidates = sum(report["candidate_count"] for report in reports)
    if total_candidates == 0:
        raise RuntimeError("As buscas reais não retornaram nenhum candidato")

    print("MVP_VALIDATION_RESULT")
    print(json.dumps({"queries": reports}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
