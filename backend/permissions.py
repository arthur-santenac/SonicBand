"""Rôles dans un groupe et vérification des droits (matrice du manuel, §7).

Deux rôles : « admin » et « membre ». Le créateur d'un groupe en est admin, et un
admin peut nommer d'autres admins parmi les membres. Un groupe garde toujours au
moins un admin.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import CurrentUser
from backend.database import get_db
from backend.models import UtilisateurGroupe

ADMIN = "admin"
MEMBRE = "membre"

ROLES = (ADMIN, MEMBRE)

# Rôles autorisés à inviter un musicien, à retirer un membre ou à changer un rôle.
GESTIONNAIRES = {ADMIN}


def get_membership(
    id_grp: Annotated[int, Path()],
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> UtilisateurGroupe:
    membership = db.scalar(
        select(UtilisateurGroupe).where(
            UtilisateurGroupe.id_grp == id_grp, UtilisateurGroupe.id_user == user.id_user
        )
    )
    if membership is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Groupe introuvable.")
    return membership


Membership = Annotated[UtilisateurGroupe, Depends(get_membership)]


def require_gestionnaire(membership: Membership) -> UtilisateurGroupe:
    if membership.role not in GESTIONNAIRES:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Seuls les admins du groupe peuvent faire cette action."
        )
    return membership


GestionnaireMembership = Annotated[UtilisateurGroupe, Depends(require_gestionnaire)]


def peut_retirer(acteur: str, cible: str) -> bool:
    """Un admin retire n'importe quel autre musicien du groupe (admin ou membre)."""
    return acteur in GESTIONNAIRES and cible in ROLES
