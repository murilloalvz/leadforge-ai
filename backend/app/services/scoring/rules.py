from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

SCORE_VERSION = "automation-v1.1"


@dataclass(frozen=True)
class Rule:
    signal: str
    weight: int
    rationale: str
    predicate: Callable[[dict[str, Any]], bool]
    evidence_keys: tuple[str, ...]


def true(key: str) -> Callable[[dict[str, Any]], bool]:
    return lambda signals: signals.get(key) is True


def checked_absent(
    checked_key: str,
    present_key: str,
) -> Callable[[dict[str, Any]], bool]:
    return (
        lambda signals: signals.get(checked_key) is True
        and signals.get(present_key) is False
    )


RULES: tuple[Rule, ...] = (
    Rule(
        "whatsapp_present",
        12,
        "WhatsApp é um canal visível de entrada de leads.",
        true("whatsapp_present"),
        ("whatsapp_present",),
    ),
    Rule(
        "website_present",
        5,
        "Existe presença web própria para sustentar aquisição e integração.",
        true("website_present"),
        ("website_present",),
    ),
    Rule(
        "contact_form_present",
        6,
        "Existe formulário público que pode alimentar um fluxo estruturado.",
        true("contact_form_present"),
        ("contact_form_present",),
    ),
    Rule(
        "multiple_services",
        8,
        "Vários serviços aumentam a utilidade de qualificação e roteamento.",
        true("multiple_services"),
        ("multiple_services",),
    ),
    Rule(
        "no_visible_booking_system",
        16,
        "Uma checagem explícita não encontrou agendamento online visível.",
        checked_absent("booking_system_checked", "booking_system_present"),
        ("booking_system_checked", "booking_system_present"),
    ),
    Rule(
        "no_visible_chat_automation",
        10,
        "Uma checagem explícita não encontrou automação de chat visível.",
        checked_absent("chat_automation_checked", "chat_automation_present"),
        ("chat_automation_checked", "chat_automation_present"),
    ),
    Rule(
        "strong_demand_signal",
        14,
        "Há sinais públicos fortes de demanda ou atividade comercial.",
        true("strong_demand_signal"),
        ("strong_demand_signal",),
    ),
    Rule(
        "active_social_presence",
        8,
        "Presença social ativa sugere fluxo contínuo de interessados.",
        true("active_social_presence"),
        ("active_social_presence",),
    ),
    Rule(
        "medium_high_ticket_vertical",
        12,
        "O nicho permite capturar valor com menos conversões adicionais.",
        true("medium_high_ticket_vertical"),
        ("medium_high_ticket_vertical",),
    ),
    Rule(
        "multiple_contact_channels",
        9,
        "Múltiplos canais aumentam a necessidade de organizar o atendimento.",
        true("multiple_contact_channels"),
        ("multiple_contact_channels",),
    ),
    Rule(
        "large_enterprise",
        -20,
        "Empresas grandes tendem a exigir venda e integração mais complexas.",
        true("large_enterprise"),
        ("large_enterprise",),
    ),
    Rule(
        "advanced_visible_automation",
        -18,
        "Automação já visível reduz a urgência da oferta inicial.",
        true("advanced_visible_automation"),
        ("advanced_visible_automation",),
    ),
    Rule(
        "possibly_inactive",
        -25,
        "Sinais de inatividade reduzem a chance de oportunidade comercial útil.",
        true("possibly_inactive"),
        ("possibly_inactive",),
    ),
)

COVERAGE_WEIGHTS: dict[str, int] = {
    "whatsapp_present": 2,
    "website_present": 1,
    "contact_form_present": 1,
    "multiple_services": 1,
    "booking_system_checked": 2,
    "booking_system_present": 2,
    "chat_automation_checked": 1,
    "chat_automation_present": 1,
    "strong_demand_signal": 2,
    "active_social_presence": 1,
    "medium_high_ticket_vertical": 1,
    "multiple_contact_channels": 1,
    "large_enterprise": 1,
    "advanced_visible_automation": 2,
    "possibly_inactive": 2,
}

COVERAGE_PREREQUISITES: dict[str, str] = {
    "booking_system_present": "booking_system_checked",
    "chat_automation_present": "chat_automation_checked",
}
