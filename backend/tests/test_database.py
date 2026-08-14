import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_database
from app.models.entities import Evidence, Prospect
from app.services.prospect_identity import build_prospect_dedup_key


def test_seed_reset_replaces_children_without_duplicates() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        assert seed_database(db, reset=True) == 15
        first_evidence_count = db.scalar(select(func.count(Evidence.id)))
        assert seed_database(db, reset=True) == 15
        second_evidence_count = db.scalar(select(func.count(Evidence.id)))

        assert db.scalar(select(func.count(Prospect.id))) == 15
        assert second_evidence_count == first_evidence_count


def test_prospect_dedup_key_is_unique_in_database() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    dedup_key = build_prospect_dedup_key("Clínica Áurea", "Campinas", "SP")

    with Session(engine) as db:
        db.add(
            Prospect(
                dedup_key=dedup_key,
                name="Clínica Áurea",
                niche="Clínica de estética",
                city="Campinas",
                state="SP",
                is_fictional=True,
            )
        )
        db.commit()
        db.add(
            Prospect(
                dedup_key=dedup_key,
                name="Clinica Aurea",
                niche="Clínica de estética",
                city="Campinas",
                state="SP",
                is_fictional=True,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
