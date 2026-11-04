"""Routes des groupes : création, liste, membres et invitations.

Règles (manuel §2 et §7) :
- le créateur d'un groupe en devient le super admin ;
- le super admin et les admins invitent des musiciens par e-mail, avec ou sans compte ;
- l'invité accepte (il devient membre) ou supprime l'invitation depuis sa boîte de réception ;
- le super admin retire n'importe quel membre, un admin ne retire que les membres.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.auth import CurrentUser
from backend.database import get_db
from backend.models import Groupe, Invitation, Utilisateur, UtilisateurGroupe
from backend.permissions import (
    MEMBRE,
    SUPER_ADMIN,
    GestionnaireMembership,
    Membership,
    peut_retirer,
)
from backend.schemas import (
    GroupeIn,
    GroupeOut,
    InvitationEnvoyeeOut,
    InvitationIn,
    InvitationRecueOut,
    MembreOut,
    MembresGroupeOut,
)

router = APIRouter(prefix="/api", tags=["groupes"])

DbSession = Annotated[Session, Depends(get_db)]

EN_ATTENTE = "en_attente"
ACCEPTEE = "acceptee"
REFUSEE = "refusee"


# --- Outils -------------------------------------------------------------------


def _nb_membres(db: Session, id_grp: int) -> int:
    return db.scalar(
        select(func.count()).select_from(UtilisateurGroupe).where(UtilisateurGroupe.id_grp == id_grp)
    )


def _groupe_out(db: Session, groupe: Groupe, role: str) -> GroupeOut:
    return GroupeOut(
        id_grp=groupe.id_grp,
        nom_grp=groupe.nom_grp,
        description_grp=groupe.description_grp,
        url_photo=groupe.url_photo,
        date_crea_grp=groupe.date_crea_grp,
        nb_membres=_nb_membres(db, groupe.id_grp),
        mon_role=role,
    )


def _invitations_pour(user: Utilisateur):
    """Filtre des invitations en attente adressées à cet utilisateur (par compte ou par e-mail)."""
    return (
        Invitation.statut == EN_ATTENTE,
        or_(Invitation.id_user == user.id_user, Invitation.email_invit == user.email_user.lower()),
    )


def _get_invitation_recue(db: Session, id_invit: int, user: Utilisateur) -> Invitation:
    invitation = db.scalar(
        select(Invitation).where(Invitation.id_invit == id_invit, *_invitations_pour(user))
    )
    if invitation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invitation introuvable.")
    return invitation


# --- Groupes ------------------------------------------------------------------


@router.post("/groupes", response_model=GroupeOut, status_code=status.HTTP_201_CREATED)
def creer_groupe(data: GroupeIn, user: CurrentUser, db: DbSession) -> GroupeOut:
    groupe = Groupe(nom_grp=data.nom, description_grp=data.description)
    db.add(groupe)
    db.flush()
    db.add(UtilisateurGroupe(id_user=user.id_user, id_grp=groupe.id_grp, role=SUPER_ADMIN))
    db.commit()
    db.refresh(groupe)
    return _groupe_out(db, groupe, SUPER_ADMIN)


@router.get("/groupes", response_model=list[GroupeOut])
def mes_groupes(user: CurrentUser, db: DbSession) -> list[GroupeOut]:
    rows = db.execute(
        select(Groupe, UtilisateurGroupe.role)
        .join(UtilisateurGroupe, UtilisateurGroupe.id_grp == Groupe.id_grp)
        .where(UtilisateurGroupe.id_user == user.id_user)
        .order_by(Groupe.date_crea_grp, Groupe.id_grp)
    ).all()
    return [_groupe_out(db, groupe, role) for groupe, role in rows]


@router.get("/groupes/{id_grp}", response_model=GroupeOut)
def detail_groupe(id_grp: int, membership: Membership, db: DbSession) -> GroupeOut:
    return _groupe_out(db, db.get(Groupe, id_grp), membership.role)


# --- Membres ------------------------------------------------------------------


@router.get("/groupes/{id_grp}/membres", response_model=MembresGroupeOut)
def membres_groupe(id_grp: int, membership: Membership, db: DbSession) -> MembresGroupeOut:
    ordre_role = {SUPER_ADMIN: 0, "admin": 1, MEMBRE: 2}
    rows = db.execute(
        select(UtilisateurGroupe, Utilisateur)
        .join(Utilisateur, Utilisateur.id_user == UtilisateurGroupe.id_user)
        .where(UtilisateurGroupe.id_grp == id_grp)
        .order_by(UtilisateurGroupe.date_rejoint, Utilisateur.id_user)
    ).all()
    membres = sorted(
        (
            MembreOut(
                id_user=u.id_user,
                nom_user=u.nom_user,
                email_user=u.email_user,
                role=ug.role or MEMBRE,
                date_rejoint=ug.date_rejoint,
            )
            for ug, u in rows
        ),
        key=lambda m: ordre_role.get(m.role, 3),
    )

    invitations = db.execute(
        select(Invitation, Utilisateur.nom_user)
        .outerjoin(Utilisateur, Utilisateur.id_user == Invitation.id_user)
        .where(Invitation.id_grp == id_grp, Invitation.statut == EN_ATTENTE)
        .order_by(Invitation.date_invit, Invitation.id_invit)
    ).all()
    return MembresGroupeOut(
        membres=membres,
        invitations=[
            InvitationEnvoyeeOut(
                id_invit=inv.id_invit,
                email_invit=inv.email_invit,
                nom_user=nom,
                date_invit=inv.date_invit,
            )
            for inv, nom in invitations
        ],
    )


@router.delete("/groupes/{id_grp}/membres/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
def retirer_membre(
    id_grp: int, id_user: int, membership: GestionnaireMembership, db: DbSession
) -> Response:
    cible = db.get(UtilisateurGroupe, (id_user, id_grp))
    if cible is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ce musicien ne fait pas partie du groupe.")
    if not peut_retirer(membership.role, cible.role or MEMBRE):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tu ne peux pas retirer ce musicien.")
    db.delete(cible)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Invitations (côté groupe) -----------------------------------------------


@router.post(
    "/groupes/{id_grp}/invitations",
    response_model=InvitationEnvoyeeOut,
    status_code=status.HTTP_201_CREATED,
)
def inviter(
    id_grp: int,
    data: InvitationIn,
    membership: GestionnaireMembership,
    db: DbSession,
) -> InvitationEnvoyeeOut:
    email = data.email.lower()
    invite = db.scalar(select(Utilisateur).where(func.lower(Utilisateur.email_user) == email))

    if invite is not None and db.get(UtilisateurGroupe, (invite.id_user, id_grp)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ce musicien fait déjà partie du groupe.")

    deja_invite = db.scalar(
        select(Invitation).where(
            Invitation.id_grp == id_grp,
            Invitation.email_invit == email,
            Invitation.statut == EN_ATTENTE,
        )
    )
    if deja_invite is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Une invitation est déjà en attente pour cet e-mail.")

    invitation = Invitation(
        id_grp=id_grp,
        email_invit=email,
        id_user=invite.id_user if invite else None,
        invite_par=membership.id_user,
        statut=EN_ATTENTE,
    )
    db.add(invitation)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Une invitation est déjà en attente pour cet e-mail.")
    db.refresh(invitation)
    return InvitationEnvoyeeOut(
        id_invit=invitation.id_invit,
        email_invit=invitation.email_invit,
        nom_user=invite.nom_user if invite else None,
        date_invit=invitation.date_invit,
    )


@router.delete(
    "/groupes/{id_grp}/invitations/{id_invit}", status_code=status.HTTP_204_NO_CONTENT
)
def annuler_invitation(
    id_grp: int, id_invit: int, membership: GestionnaireMembership, db: DbSession
) -> Response:
    invitation = db.scalar(
        select(Invitation).where(
            Invitation.id_invit == id_invit,
            Invitation.id_grp == id_grp,
            Invitation.statut == EN_ATTENTE,
        )
    )
    if invitation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invitation introuvable.")
    db.delete(invitation)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Invitations (boîte de réception de l'invité) ----------------------------


@router.get("/invitations", response_model=list[InvitationRecueOut])
def mes_invitations(user: CurrentUser, db: DbSession) -> list[InvitationRecueOut]:
    rows = db.execute(
        select(Invitation, Groupe.nom_grp, Utilisateur.nom_user)
        .join(Groupe, Groupe.id_grp == Invitation.id_grp)
        .outerjoin(Utilisateur, Utilisateur.id_user == Invitation.invite_par)
        .where(*_invitations_pour(user))
        .order_by(Invitation.date_invit.desc(), Invitation.id_invit.desc())
    ).all()
    return [
        InvitationRecueOut(
            id_invit=inv.id_invit,
            id_grp=inv.id_grp,
            nom_grp=nom_grp,
            invite_par=nom_inviteur,
            date_invit=inv.date_invit,
        )
        for inv, nom_grp, nom_inviteur in rows
    ]


@router.post("/invitations/{id_invit}/accepter", response_model=GroupeOut)
def accepter_invitation(id_invit: int, user: CurrentUser, db: DbSession) -> GroupeOut:
    invitation = _get_invitation_recue(db, id_invit, user)
    invitation.statut = ACCEPTEE
    invitation.id_user = user.id_user

    membership = db.get(UtilisateurGroupe, (user.id_user, invitation.id_grp))
    if membership is None:
        membership = UtilisateurGroupe(id_user=user.id_user, id_grp=invitation.id_grp, role=MEMBRE)
        db.add(membership)
    db.commit()
    return _groupe_out(db, db.get(Groupe, invitation.id_grp), membership.role or MEMBRE)


@router.post("/invitations/{id_invit}/refuser", status_code=status.HTTP_204_NO_CONTENT)
def refuser_invitation(id_invit: int, user: CurrentUser, db: DbSession) -> Response:
    invitation = _get_invitation_recue(db, id_invit, user)
    invitation.statut = REFUSEE
    invitation.id_user = user.id_user
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)