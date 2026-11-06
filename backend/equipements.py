"""Routes des équipements personnels et partagés avec un groupe."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import CurrentUser
from backend.database import get_db
from backend.models import (
    EvenementEquipement,
    Equipement,
    Groupe,
    GroupeEquipement,
    Utilisateur,
    UtilisateurEquipement,
    UtilisateurGroupe,
)
from backend.permissions import Membership
from backend.schemas import EquipementIn, EquipementOut

router = APIRouter(prefix="/api", tags=["équipements"])
DbSession = Annotated[Session, Depends(get_db)]


def _supprimer_si_orphelin(db: Session, equipement: Equipement) -> None:
    references = (
        select(UtilisateurEquipement.id_equipement).where(
            UtilisateurEquipement.id_equipement == equipement.id_equipement
        ),
        select(GroupeEquipement.id_equipement).where(
            GroupeEquipement.id_equipement == equipement.id_equipement
        ),
        select(EvenementEquipement.id_equipement).where(
            EvenementEquipement.id_equipement == equipement.id_equipement
        ),
    )
    if not any(db.scalar(reference) is not None for reference in references):
        db.delete(equipement)


@router.get("/groupes/{id_grp}/equipements", response_model=list[EquipementOut])
def lister_equipements_groupe(
    id_grp: int, _membership: Membership, db: DbSession
) -> list[EquipementOut]:
    result: dict[int, EquipementOut] = {}
    group_rows = db.execute(
        select(Equipement, Groupe.nom_grp)
        .join(GroupeEquipement, GroupeEquipement.id_equipement == Equipement.id_equipement)
        .join(Groupe, Groupe.id_grp == GroupeEquipement.id_grp)
        .where(GroupeEquipement.id_grp == id_grp)
        .order_by(Equipement.nom_equipement, Equipement.id_equipement)
    ).all()
    for equipement, nom_groupe in group_rows:
        result[equipement.id_equipement] = EquipementOut(
            id_equipement=equipement.id_equipement,
            nom_equipement=equipement.nom_equipement,
            proprietaire=nom_groupe,
            est_equipement_groupe=True,
        )

    personal_rows = db.execute(
        select(Equipement, Utilisateur.nom_user)
        .join(
            UtilisateurEquipement,
            UtilisateurEquipement.id_equipement == Equipement.id_equipement,
        )
        .join(Utilisateur, Utilisateur.id_user == UtilisateurEquipement.id_user)
        .join(UtilisateurGroupe, UtilisateurGroupe.id_user == Utilisateur.id_user)
        .where(
            UtilisateurGroupe.id_grp == id_grp,
            ~select(GroupeEquipement.id_equipement)
            .where(
                GroupeEquipement.id_grp == id_grp,
                GroupeEquipement.id_equipement == Equipement.id_equipement,
            )
            .exists(),
        )
        .order_by(Equipement.nom_equipement, Utilisateur.nom_user)
    ).all()
    for equipement, nom_user in personal_rows:
        current = result.get(equipement.id_equipement)
        if current is None:
            result[equipement.id_equipement] = EquipementOut(
                id_equipement=equipement.id_equipement,
                nom_equipement=equipement.nom_equipement,
                proprietaire=nom_user,
            )
        elif nom_user not in (current.proprietaire or "").split(", "):
            current.proprietaire = f"{current.proprietaire}, {nom_user}"

    return sorted(
        result.values(),
        key=lambda item: (item.nom_equipement.lower(), item.id_equipement),
    )


@router.post(
    "/groupes/{id_grp}/equipements",
    response_model=EquipementOut,
    status_code=status.HTTP_201_CREATED,
)
def ajouter_equipement_groupe(
    id_grp: int, data: EquipementIn, _membership: Membership, db: DbSession
) -> EquipementOut:
    groupe = db.get(Groupe, id_grp)
    equipement = Equipement(nom_equipement=data.nom_equipement)
    db.add(equipement)
    db.flush()
    db.add(GroupeEquipement(id_grp=groupe.id_grp, id_equipement=equipement.id_equipement))
    db.commit()
    db.refresh(equipement)
    return EquipementOut(
        id_equipement=equipement.id_equipement,
        nom_equipement=equipement.nom_equipement,
        proprietaire=groupe.nom_grp,
        est_equipement_groupe=True,
    )


@router.delete(
    "/groupes/{id_grp}/equipements/{id_equipement}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def retirer_equipement_groupe(
    id_grp: int,
    id_equipement: int,
    _membership: Membership,
    db: DbSession,
) -> Response:
    association = db.get(GroupeEquipement, (id_grp, id_equipement))
    if association is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Cet équipement n'appartient pas au groupe."
        )
    equipement = db.get(Equipement, id_equipement)
    db.delete(association)
    _supprimer_si_orphelin(db, equipement)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/equipements/personnels", response_model=list[EquipementOut])
def lister_equipements_personnels(user: CurrentUser, db: DbSession) -> list[EquipementOut]:
    rows = db.execute(
        select(Equipement)
        .join(
            UtilisateurEquipement,
            UtilisateurEquipement.id_equipement == Equipement.id_equipement,
        )
        .where(UtilisateurEquipement.id_user == user.id_user)
        .order_by(Equipement.nom_equipement, Equipement.id_equipement)
    ).scalars()
    return [
        EquipementOut(
            id_equipement=equipement.id_equipement,
            nom_equipement=equipement.nom_equipement,
        )
        for equipement in rows
    ]


@router.post(
    "/equipements/personnels",
    response_model=EquipementOut,
    status_code=status.HTTP_201_CREATED,
)
def ajouter_equipement_personnel(
    data: EquipementIn, user: CurrentUser, db: DbSession
) -> EquipementOut:
    equipement = Equipement(nom_equipement=data.nom_equipement)
    db.add(equipement)
    db.flush()
    db.add(
        UtilisateurEquipement(
            id_user=user.id_user,
            id_equipement=equipement.id_equipement,
        )
    )
    db.commit()
    db.refresh(equipement)
    return EquipementOut(
        id_equipement=equipement.id_equipement,
        nom_equipement=equipement.nom_equipement,
    )


@router.delete(
    "/equipements/personnels/{id_equipement}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def retirer_equipement_personnel(
    id_equipement: int, user: CurrentUser, db: DbSession
) -> Response:
    association = db.get(UtilisateurEquipement, (user.id_user, id_equipement))
    if association is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Équipement personnel introuvable.")
    equipement = db.get(Equipement, id_equipement)
    db.delete(association)
    _supprimer_si_orphelin(db, equipement)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
