"""Rôles dans un groupe et vérification des droits (matrice du manuel, §7)."""

from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import CurrentUser
from backend.database import get_db
from backend.models import UtilisateurGroupe

SUPER_ADMIN = "super_admin"
ADMIN = "admin"
MEMBRE = "membre"

# Rôles autorisés à inviter un musicien ou à retirer un membre.
GESTIONNAIRES = {SUPER_ADMIN, ADMIN}


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
    """Le super admin retire n'importe qui (sauf lui-même) ; un admin ne retire que des membres."""
    if cible == SUPER_ADMIN:
        return False
    if acteur == SUPER_ADMIN:
        return True
    return acteur == ADMIN and cible == MEMBRE