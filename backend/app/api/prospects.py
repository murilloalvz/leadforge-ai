from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.entities import Prospect
from app.schemas.prospect import ProspectDetail, ProspectSummary

router = APIRouter(prefix="/prospects", tags=["prospects"])


@router.get("", response_model=list[ProspectSummary])
def list_prospects(
    min_score: int | None = Query(default=None, ge=0, le=100),
    city: str | None = None,
    db: Session = Depends(get_db),
) -> list[Prospect]:
    statement = select(Prospect).order_by(Prospect.score.desc().nullslast(), Prospect.name)
    if min_score is not None:
        statement = statement.where(Prospect.score >= min_score)
    if city:
        statement = statement.where(Prospect.city == city)
    return list(db.scalars(statement).all())


@router.get("/{prospect_id}", response_model=ProspectDetail)
def get_prospect(prospect_id: int, db: Session = Depends(get_db)) -> Prospect:
    statement = (
        select(Prospect)
        .where(Prospect.id == prospect_id)
        .options(selectinload(Prospect.evidence), selectinload(Prospect.score_components))
    )
    prospect = db.scalar(statement)
    if prospect is None:
        raise HTTPException(status_code=404, detail="Prospect não encontrado")
    return prospect
