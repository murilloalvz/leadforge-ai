from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.entities import Evidence, Prospect, ScoreComponent
from app.services.scoring.engine import OpportunityScorer


FICTIONAL_PROSPECTS = [
    ("Clínica Aurora", "Campinas", {"whatsapp_present": True, "website_present": True, "contact_form_present": True, "multiple_services": True, "booking_system_checked": True, "booking_system_present": False, "chat_automation_checked": True, "chat_automation_present": False, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True, "large_enterprise": False, "advanced_visible_automation": False, "possibly_inactive": False}),
    ("Estética Lumi", "Campinas", {"whatsapp_present": True, "website_present": True, "contact_form_present": False, "multiple_services": True, "booking_system_checked": True, "booking_system_present": False, "chat_automation_checked": True, "chat_automation_present": False, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True, "large_enterprise": False, "advanced_visible_automation": False, "possibly_inactive": False}),
    ("Viva Derma", "Campinas", {"whatsapp_present": True, "website_present": True, "multiple_services": True, "booking_system_checked": True, "booking_system_present": True, "chat_automation_checked": True, "chat_automation_present": True, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True, "advanced_visible_automation": True, "large_enterprise": False, "possibly_inactive": False}),
    ("Studio Serena", "Valinhos", {"whatsapp_present": True, "website_present": False, "multiple_services": True, "booking_system_checked": True, "booking_system_present": False, "chat_automation_checked": True, "chat_automation_present": False, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": False, "large_enterprise": False, "advanced_visible_automation": False, "possibly_inactive": False}),
    ("Essenza Clinic", "São Paulo", {"whatsapp_present": True, "website_present": True, "contact_form_present": True, "multiple_services": True, "booking_system_checked": True, "booking_system_present": True, "chat_automation_checked": True, "chat_automation_present": True, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True, "large_enterprise": True, "advanced_visible_automation": True, "possibly_inactive": False}),
    ("Ateliê Bela Pele", "Campinas", {"whatsapp_present": True, "website_present": False, "multiple_services": True, "booking_system_checked": True, "booking_system_present": False, "chat_automation_checked": False, "strong_demand_signal": False, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": False, "large_enterprise": False, "advanced_visible_automation": False, "possibly_inactive": False}),
    ("Clínica Harmonia", "Jundiaí", {"whatsapp_present": True, "website_present": True, "contact_form_present": True, "multiple_services": True, "booking_system_checked": True, "booking_system_present": False, "chat_automation_checked": True, "chat_automation_present": False, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True, "large_enterprise": False, "advanced_visible_automation": False, "possibly_inactive": False}),
    ("Espaço Íris", "Campinas", {"whatsapp_present": True, "website_present": False, "multiple_services": False, "booking_system_checked": True, "booking_system_present": False, "active_social_presence": False, "medium_high_ticket_vertical": True, "possibly_inactive": True}),
    ("Maison Derm", "São Paulo", {"whatsapp_present": True, "website_present": True, "contact_form_present": True, "multiple_services": True, "booking_system_checked": True, "booking_system_present": True, "chat_automation_checked": True, "chat_automation_present": True, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True, "large_enterprise": False, "advanced_visible_automation": True, "possibly_inactive": False}),
    ("Bella Forma", "Sumaré", {"whatsapp_present": True, "website_present": True, "multiple_services": True, "booking_system_checked": True, "booking_system_present": False, "chat_automation_checked": True, "chat_automation_present": False, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True, "possibly_inactive": False}),
    ("Nuance Estética", "Campinas", {"whatsapp_present": True, "website_present": True, "multiple_services": True, "booking_system_checked": False, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True}),
    ("Pele & Luz", "Hortolândia", {"whatsapp_present": True, "website_present": False, "multiple_services": True, "booking_system_checked": True, "booking_system_present": False, "chat_automation_checked": True, "chat_automation_present": False, "strong_demand_signal": False, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": False}),
    ("Clínica Prisma", "Campinas", {"website_present": True, "contact_form_present": True, "multiple_services": True, "booking_system_checked": True, "booking_system_present": True, "chat_automation_checked": True, "chat_automation_present": False, "strong_demand_signal": True, "active_social_presence": True, "medium_high_ticket_vertical": True, "multiple_contact_channels": True}),
    ("Estética Orquídea", "Paulínia", {"whatsapp_present": True, "website_present": False, "multiple_services": True, "active_social_presence": True, "medium_high_ticket_vertical": True}),
    ("Studio Horizonte", "Campinas", {"whatsapp_present": False, "website_present": False, "multiple_services": False, "possibly_inactive": True}),
]


def seed_database(db: Session, reset: bool = False) -> int:
    if reset:
        db.execute(delete(Prospect))
        db.commit()
    elif db.scalar(select(Prospect.id).limit(1)) is not None:
        return 0

    scorer = OpportunityScorer()
    created = 0
    for index, (name, city, signals) in enumerate(FICTIONAL_PROSPECTS, start=1):
        result = scorer.score(signals)
        prospect = Prospect(
            name=name,
            niche="Clínica de estética",
            city=city,
            state="SP",
            website=f"https://demo{index}.invalid" if signals.get("website_present") else None,
            phone=f"+55 19 90000-{index:04d}" if signals.get("whatsapp_present") else None,
            is_fictional=True,
            score=result.total,
            score_confidence=result.confidence,
        )
        db.add(prospect)
        db.flush()

        for key, value in signals.items():
            db.add(Evidence(prospect_id=prospect.id, key=key, value=value, source="seed:fictional", confidence=1.0))
        for component in result.components:
            db.add(ScoreComponent(prospect_id=prospect.id, signal=component.signal, value=component.value, weight=component.weight, contribution=component.contribution, rationale=component.rationale))
        created += 1
    db.commit()
    return created


if __name__ == "__main__":
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        print(f"Prospects fictícios criados: {seed_database(session)}")
