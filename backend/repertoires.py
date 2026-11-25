"""Routes des répertoires et morceaux des groupes.

Chaque morceau peut recevoir des pièces jointes (partition, tablature, maquette
audio, paroles…), utiles quand il n'y a pas de lien YouTube par exemple.
"""

from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload, undefer

from backend.database import get_db
from backend.models import Morceau, PieceJointe, Repertoire, RepertoireMorceau
from backend.permissions import Membership
from backend.schemas import (
    MorceauIn,
    MorceauOut,
    PieceJointeOut,
    RepertoireIn,
    RepertoireOut,
)

# Taille maximale d'une pièce jointe et nombre maximal de pièces par morceau.
TAILLE_MAX_PJ = 10 * 1024 * 1024
NB_MAX_PJ = 10

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
        .options(selectinload(Morceau.pieces_jointes))
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
        morceaux=[_morceau_out(morceau, association.position) for association, morceau in rows],
    )


def _morceau_out(morceau: Morceau, position: int | None) -> MorceauOut:
    return MorceauOut(
        id_song=morceau.id_song,
        titre_song=morceau.titre_song,
        compositeur=morceau.compositeur,
        lien_youtube=morceau.lien_youtube,
        url_img=morceau.url_img,
        position=position,
        pieces_jointes=[PieceJointeOut.model_validate(pj) for pj in morceau.pieces_jointes],
    )


def _get_morceau(db: Session, id_grp: int, id_rep: int, id_song: int) -> Morceau:
    """Morceau présent dans un répertoire du groupe, sinon 404."""
    repertoire = _get_repertoire(db, id_grp, id_rep)
    if db.get(RepertoireMorceau, (repertoire.id_rep, id_song)) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Morceau introuvable dans ce répertoire.")
    return db.get(Morceau, id_song)


def _get_piece_jointe(
    db: Session, id_grp: int, id_rep: int, id_song: int, id_pj: int, *, avec_contenu: bool = False
) -> PieceJointe:
    _get_morceau(db, id_grp, id_rep, id_song)
    requete = select(PieceJointe).where(PieceJointe.id_pj == id_pj, PieceJointe.id_song == id_song)
    if avec_contenu:
        requete = requete.options(undefer(PieceJointe.contenu))
    piece = db.scalar(requete)
    if piece is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pièce jointe introuvable.")
    return piece


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
    return _morceau_out(morceau, position)


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
    db.flush()
    # Un morceau qui n'est plus dans aucun répertoire est supprimé avec ses pièces jointes.
    encore_utilise = db.scalar(
        select(func.count()).select_from(RepertoireMorceau).where(RepertoireMorceau.id_song == id_song)
    )
    if not encore_utilise:
        db.execute(PieceJointe.__table__.delete().where(PieceJointe.id_song == id_song))
        db.execute(Morceau.__table__.delete().where(Morceau.id_song == id_song))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Pièces jointes -----------------------------------------------------------


@router.post(
    "/repertoires/{id_rep}/morceaux/{id_song}/pieces-jointes",
    response_model=list[PieceJointeOut],
    status_code=status.HTTP_201_CREATED,
)
async def ajouter_pieces_jointes(
    id_grp: int,
    id_rep: int,
    id_song: int,
    _membership: Membership,
    db: DbSession,
    fichiers: Annotated[list[UploadFile], File(description="Un ou plusieurs fichiers")],
) -> list[PieceJointeOut]:
    morceau = _get_morceau(db, id_grp, id_rep, id_song)
    deja = len(morceau.pieces_jointes)
    if deja + len(fichiers) > NB_MAX_PJ:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Un morceau peut avoir au plus {NB_MAX_PJ} pièces jointes.",
        )

    pieces = []
    for fichier in fichiers:
        nom = (fichier.filename or "fichier").replace("\\", "/").rsplit("/", 1)[-1].strip()[:255]
        contenu = await fichier.read(TAILLE_MAX_PJ + 1)
        if len(contenu) > TAILLE_MAX_PJ:
            raise HTTPException(
                status.HTTP_413_CONTENT_TOO_LARGE,
                f"« {nom} » dépasse la taille maximale de {TAILLE_MAX_PJ // (1024 * 1024)} Mo.",
            )
        if not contenu:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"« {nom} » est vide.")
        pieces.append(
            PieceJointe(
                id_song=morceau.id_song,
                nom_fichier=nom or "fichier",
                type_mime=(fichier.content_type or "application/octet-stream")[:255],
                taille=len(contenu),
                contenu=contenu,
            )
        )
    db.add_all(pieces)
    db.commit()
    return [PieceJointeOut.model_validate(piece) for piece in pieces]


@router.get("/repertoires/{id_rep}/morceaux/{id_song}/pieces-jointes/{id_pj}")
def telecharger_piece_jointe(
    id_grp: int,
    id_rep: int,
    id_song: int,
    id_pj: int,
    _membership: Membership,
    db: DbSession,
) -> Response:
    piece = _get_piece_jointe(db, id_grp, id_rep, id_song, id_pj, avec_contenu=True)
    return Response(
        content=piece.contenu,
        media_type=piece.type_mime,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(piece.nom_fichier)}",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete(
    "/repertoires/{id_rep}/morceaux/{id_song}/pieces-jointes/{id_pj}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def supprimer_piece_jointe(
    id_grp: int,
    id_rep: int,
    id_song: int,
    id_pj: int,
    _membership: Membership,
    db: DbSession,
) -> Response:
    piece = _get_piece_jointe(db, id_grp, id_rep, id_song, id_pj)
    db.delete(piece)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
