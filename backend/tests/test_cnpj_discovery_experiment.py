from __future__ import annotations

import csv
from pathlib import Path

from scripts.experiment_cnpj_dentists import (
    DENTISTRY_CNAE,
    build_report,
    find_active_businesses,
    load_municipality_codes,
)


def _write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="latin-1", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerows(rows)


def _establishment_row(
    *,
    basic: str,
    order: str,
    check_digits: str,
    trade_name: str,
    status: str,
    primary_cnae: str,
    secondary_cnae: str,
    state: str,
    municipality_code: str,
) -> list[str]:
    row = [""] * 30
    row[0] = basic
    row[1] = order
    row[2] = check_digits
    row[4] = trade_name
    row[5] = status
    row[11] = primary_cnae
    row[12] = secondary_cnae
    row[19] = state
    row[20] = municipality_code
    return row


def test_filters_active_dentistry_establishments_in_target_city(tmp_path: Path) -> None:
    municipalities = tmp_path / "Municipios.csv"
    establishments = tmp_path / "Estabelecimentos.csv"
    _write_rows(
        municipalities,
        [
            ["6619", "JUNDIAI"],
            ["6291", "CAMPINAS"],
        ],
    )
    _write_rows(
        establishments,
        [
            _establishment_row(
                basic="12345678",
                order="0001",
                check_digits="90",
                trade_name="Odonto Centro",
                status="02",
                primary_cnae=DENTISTRY_CNAE,
                secondary_cnae="",
                state="SP",
                municipality_code="6619",
            ),
            _establishment_row(
                basic="ABCDEFGH",
                order="0001",
                check_digits="XY",
                trade_name="Clínica Saúde",
                status="02",
                primary_cnae="8630503",
                secondary_cnae=f"8630501,{DENTISTRY_CNAE}",
                state="SP",
                municipality_code="6619",
            ),
            _establishment_row(
                basic="99999999",
                order="0001",
                check_digits="00",
                trade_name="Dentista Inativo",
                status="08",
                primary_cnae=DENTISTRY_CNAE,
                secondary_cnae="",
                state="SP",
                municipality_code="6619",
            ),
            _establishment_row(
                basic="11111111",
                order="0001",
                check_digits="11",
                trade_name="Dentista Campinas",
                status="02",
                primary_cnae=DENTISTRY_CNAE,
                secondary_cnae="",
                state="SP",
                municipality_code="6291",
            ),
        ],
    )

    municipality_codes = load_municipality_codes(municipalities, "Jundiaí")
    matches = find_active_businesses(
        [establishments],
        municipality_codes,
        "SP",
    )

    assert [match.trade_name for match in matches] == ["Odonto Centro", "Clínica Saúde"]
    assert [match.match_source for match in matches] == ["primary", "secondary"]
    assert matches[1].cnpj == "ABCDEFGH0001XY"

    report = build_report(matches, "Jundiaí", "SP", DENTISTRY_CNAE, sample_limit=10)
    assert report["active_business_count"] == 2
    assert report["primary_cnae_count"] == 1
    assert report["secondary_cnae_count"] == 1


def test_raises_when_city_is_not_present(tmp_path: Path) -> None:
    municipalities = tmp_path / "Municipios.csv"
    _write_rows(municipalities, [["6619", "JUNDIAI"]])

    try:
        load_municipality_codes(municipalities, "Sorocaba")
    except ValueError as exc:
        assert "Sorocaba" in str(exc)
    else:
        raise AssertionError("Era esperado ValueError para município ausente")
