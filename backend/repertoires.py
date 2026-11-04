"""Routes des répertoires et morceaux des groupes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Morceau, Repertoire, RepertoireMorceau
from backend.permissions import Membership
from backend.schemas import (
    MorceauIn,
    MorceauOut,
    RepertoireIn,
    RepertoireOut,
)

router = APIRouter(prefix="/api/groupes/{id_grp}", tags=["répertoires"])
DbSession = Annotated[Session, Depends(get_db)]


def _get_repertoire(db: Session, id_grp: int, id_rep: int) -> Repertoire:
    repertoire = db.scalar(
        select(Repertoire).where(
            Repertoire.id_rep == id_rep,
            Repertoire.id_grp == id_grp,
        )
    )
    if repertoire is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Répertoire introuvable.")
    return repertoire


def _repertoire_out(db: Session, repertoire: Repertoire) -> RepertoireOut:
    rows = db.execute(
        select(RepertoireMorceau, Morceau)
        .join(Morceau, Morceau.id_song == RepertoireMorceau.id_song)
        .where(RepertoireMorceau.id_rep == repertoire.id_rep)
        .order_by(
            RepertoireMorceau.position.is_(None),
            RepertoireMorceau.position,
            Morceau.titre_song,
        )
    ).all()
    return RepertoireOut(
        id_rep=repertoire.id_rep,
        nom_rep=repertoire.nom_rep,
        morceaux=[
            MorceauOut(
                id_song=morceau.id_song,
                titre_song=morceau.titre_song,
                compositeur=morceau.compositeur,
                lien_youtube=morceau.lien_youtube,
                url_img=morceau.url_img,
                position=association.position,
            )
            for association, morceau in rows
        ],
    )


@router.get("/repertoires", response_model=list[RepertoireOut])
def lister_repertoires(
    id_grp: int, _membership: Membership, db: DbSession
) -> list[RepertoireOut]:
    repertoires = db.scalars(
        select(Repertoire)
        .where(Repertoire.id_grp == id_grp)
        .order_by(Repertoire.id_rep)
    ).all()
    return [_repertoire_out(db, repertoire) for repertoire in repertoires]


@router.post(
    "/repertoires",
    response_model=RepertoireOut,
    status_code=status.HTTP_201_CREATED,
)
def creer_repertoire(
    id_grp: int, data: RepertoireIn, _membership: Membership, db: DbSession
) -> RepertoireOut:
    repertoire = Repertoire(nom_rep=data.nom_rep, id_grp=id_grp)
    db.add(repertoire)
    db.commit()
    db.refresh(repertoire)
    return _repertoire_out(db, repertoire)


@router.post(
    "/repertoires/{id_rep}/morceaux",
    response_model=MorceauOut,
    status_code=status.HTTP_201_CREATED,
)
def ajouter_morceau(
    id_grp: int,
    id_rep: int,
    data: MorceauIn,
    _membership: Membership,
    db: DbSession,
) -> MorceauOut:
    repertoire = _get_repertoire(db, id_grp, id_rep)
    morceau = Morceau(
        titre_song=data.titre_song,
        compositeur=data.compositeur,
        lien_youtube=data.lien_youtube,
        url_img=data.url_img,
    )
    db.add(morceau)
    db.flush()
    position = (
        db.scalar(
            select(func.coalesce(func.max(RepertoireMorceau.position), 0)).where(
                RepertoireMorceau.id_rep == repertoire.id_rep
            )
        )
        + 1
    )
    db.add(
        RepertoireMorceau(
            id_rep=repertoire.id_rep,
            id_song=morceau.id_song,
            position=position,
        )
    )
    db.commit()
    db.refresh(morceau)
    return MorceauOut(
        id_song=morceau.id_song,
        titre_song=morceau.titre_song,
        compositeur=morceau.compositeur,
        lien_youtube=morceau.lien_youtube,
        url_img=morceau.url_img,
        position=position,
    )


@router.delete(
    "/repertoires/{id_rep}/morceaux/{id_song}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def retirer_morceau(
    id_grp: int,
    id_rep: int,
    id_song: int,
    _membership: Membership,
    db: DbSession,
) -> Response:
    repertoire = _get_repertoire(db, id_grp, id_rep)
    association = db.get(RepertoireMorceau, (repertoire.id_rep, id_song))
    if association is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Morceau introuvable dans ce répertoire.")
    db.delete(association)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
