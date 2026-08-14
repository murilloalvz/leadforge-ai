from app.services.prospect_identity import build_prospect_dedup_key


def test_dedup_key_normalizes_case_accents_and_whitespace() -> None:
    first = build_prospect_dedup_key("Clínica  Áurea", "São Paulo", "sp")
    second = build_prospect_dedup_key("clinica aurea", "sao   paulo", "SP")
    assert first == second


def test_dedup_key_changes_for_another_city() -> None:
    first = build_prospect_dedup_key("Clínica Áurea", "São Paulo", "SP")
    second = build_prospect_dedup_key("Clínica Áurea", "Campinas", "SP")
    assert first != second
