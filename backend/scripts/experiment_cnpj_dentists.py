from __future__ import annotations

import argparse
import csv
import io
import json
import unicodedata
import zipfile
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path

ACTIVE_REGISTRATION_STATUS = "02"
DENTISTRY_CNAE = "8630504"

# Layout do arquivo Estabelecimentos dos dados abertos do CNPJ.
CNPJ_BASIC = 0
CNPJ_ORDER = 1
CNPJ_CHECK_DIGITS = 2
TRADE_NAME = 4
REGISTRATION_STATUS = 5
PRIMARY_CNAE = 11
SECONDARY_CNAE = 12
STATE = 19
MUNICIPALITY_CODE = 20


@dataclass(frozen=True)
class CnpjMatch:
    cnpj: str
    trade_name: str | None
    state: str
    municipality_code: str
    primary_cnae: str
    match_source: str


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip())
    return "".join(char for char in normalized if not unicodedata.combining(char)).casefold()


def _iter_csv_rows(path: Path) -> Iterator[list[str]]:
    if path.suffix.casefold() == ".zip":
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                with archive.open(member) as raw:
                    with io.TextIOWrapper(raw, encoding="latin-1", newline="") as text:
                        yield from csv.reader(text, delimiter=";")
        return

    with path.open(encoding="latin-1", newline="") as handle:
        yield from csv.reader(handle, delimiter=";")


def load_municipality_codes(path: Path, city: str) -> set[str]:
    target = normalize_text(city)
    codes: set[str] = set()

    for row in _iter_csv_rows(path):
        if len(row) < 2:
            continue
        code, name = row[0].strip(), row[1].strip()
        if code and normalize_text(name) == target:
            codes.add(code)

    if not codes:
        raise ValueError(f"Município não encontrado na tabela da Receita: {city}")
    return codes


def _cnae_matches(primary: str, secondary: str, target_cnae: str) -> str | None:
    if primary.strip() == target_cnae:
        return "primary"
    secondary_codes = {item.strip() for item in secondary.split(",") if item.strip()}
    if target_cnae in secondary_codes:
        return "secondary"
    return None


def find_active_businesses(
    establishment_paths: list[Path],
    municipality_codes: set[str],
    state: str,
    target_cnae: str = DENTISTRY_CNAE,
) -> list[CnpjMatch]:
    matches: list[CnpjMatch] = []
    target_state = state.strip().upper()

    for path in establishment_paths:
        for row in _iter_csv_rows(path):
            if len(row) <= MUNICIPALITY_CODE:
                continue
            if row[REGISTRATION_STATUS].strip() != ACTIVE_REGISTRATION_STATUS:
                continue
            if row[STATE].strip().upper() != target_state:
                continue
            if row[MUNICIPALITY_CODE].strip() not in municipality_codes:
                continue

            match_source = _cnae_matches(
                row[PRIMARY_CNAE],
                row[SECONDARY_CNAE],
                target_cnae,
            )
            if match_source is None:
                continue

            cnpj = "".join(
                (
                    row[CNPJ_BASIC].strip(),
                    row[CNPJ_ORDER].strip(),
                    row[CNPJ_CHECK_DIGITS].strip(),
                )
            )
            trade_name = row[TRADE_NAME].strip() or None
            matches.append(
                CnpjMatch(
                    cnpj=cnpj,
                    trade_name=trade_name,
                    state=target_state,
                    municipality_code=row[MUNICIPALITY_CODE].strip(),
                    primary_cnae=row[PRIMARY_CNAE].strip(),
                    match_source=match_source,
                )
            )

    return matches


def build_report(
    matches: list[CnpjMatch],
    city: str,
    state: str,
    target_cnae: str,
    sample_limit: int,
) -> dict[str, object]:
    primary_count = sum(match.match_source == "primary" for match in matches)
    secondary_count = len(matches) - primary_count
    return {
        "schema_version": "cnpj-discovery-experiment-v1",
        "city": city,
        "state": state.upper(),
        "target_cnae": target_cnae,
        "active_business_count": len(matches),
        "primary_cnae_count": primary_count,
        "secondary_cnae_count": secondary_count,
        "sample": [asdict(match) for match in matches[:sample_limit]],
        "note": (
            "Experimento de cobertura com dados abertos do CNPJ; não é ainda um provider "
            "de produção do LeadForge."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filtra estabelecimentos ativos por cidade/UF e CNAE nos dados abertos do CNPJ."
    )
    parser.add_argument("--municipalities", type=Path, required=True)
    parser.add_argument("--establishments", type=Path, nargs="+", required=True)
    parser.add_argument("--city", default="Jundiaí")
    parser.add_argument("--state", default="SP")
    parser.add_argument("--cnae", default=DENTISTRY_CNAE)
    parser.add_argument("--sample-limit", type=int, default=20)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    municipality_codes = load_municipality_codes(args.municipalities, args.city)
    matches = find_active_businesses(
        args.establishments,
        municipality_codes,
        args.state,
        args.cnae,
    )
    report = build_report(matches, args.city, args.state, args.cnae, args.sample_limit)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
