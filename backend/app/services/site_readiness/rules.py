from dataclasses import dataclass


SITE_READINESS_VERSION = "ai-discoverability-v1"


@dataclass(frozen=True)
class ReadinessCriterion:
    key: str
    weight: int
    category: str
    rationale: str


CRITERIA: tuple[ReadinessCriterion, ...] = (
    ReadinessCriterion(
        "public_http_ok",
        12,
        "technical",
        "A página responde publicamente com sucesso.",
    ),
    ReadinessCriterion(
        "indexable",
        14,
        "technical",
        "O conteúdo está elegível para indexação.",
    ),
    ReadinessCriterion(
        "googlebot_allowed",
        10,
        "crawler_access",
        "Googlebot não está bloqueado.",
    ),
    ReadinessCriterion(
        "oai_searchbot_allowed",
        10,
        "crawler_access",
        "OAI-SearchBot não está bloqueado.",
    ),
    ReadinessCriterion(
        "important_content_textual",
        12,
        "content",
        "Informações importantes existem em texto acessível.",
    ),
    ReadinessCriterion(
        "business_identity_clear",
        8,
        "content",
        "Nome e identidade do negócio estão claros.",
    ),
    ReadinessCriterion(
        "services_clearly_described",
        10,
        "content",
        "Serviços são descritos de forma explícita.",
    ),
    ReadinessCriterion(
        "location_clearly_described",
        8,
        "content",
        "Localização e área atendida estão claras.",
    ),
    ReadinessCriterion(
        "descriptive_titles",
        6,
        "content",
        "Títulos ajudam a entender o assunto das páginas.",
    ),
    ReadinessCriterion(
        "structured_data_present",
        4,
        "structured_data",
        "Há dados estruturados úteis.",
    ),
    ReadinessCriterion(
        "local_business_schema",
        3,
        "structured_data",
        "O negócio usa marcação LocalBusiness apropriada.",
    ),
    ReadinessCriterion(
        "structured_data_matches_visible_content",
        3,
        "structured_data",
        "A marcação corresponde ao conteúdo visível.",
    ),
)

TOTAL_WEIGHT = sum(criterion.weight for criterion in CRITERIA)
BLOCKER_CAPS: dict[str, int] = {
    "public_http_ok": 10,
    "indexable": 25,
}
