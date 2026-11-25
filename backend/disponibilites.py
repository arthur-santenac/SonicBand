"""Routes des disponibilités (manuel §4).

Les disponibilités appartiennent à l'utilisateur, pas au groupe : les mêmes plages
servent pour tous ses groupes. Une plage est soit ponctuelle (une date), soit dans
le planning type (chaque semaine à partir d'une date). Une plage du planning type
peut être retirée pour une seule semaine.

Le calendrier du groupe superpose les plages de tous ses membres : chaque créneau
renvoyé indique qui est libre, le frontend fonce le bleu selon ce nombre.
"""

from datetime import date, time, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from backend.auth import CurrentUser
from backend.database import get_db
from backend.models import Disponibilite, Utilisateur, UtilisateurGroupe
from backend.permissions import Membership
from backend.schemas import (
    DEBUT_JOURNEE,
    FIN_JOURNEE,
    CreneauGroupeOut,
    DisponibiliteIn,
    DisponibilitesGroupeOut,
    DisponibiliteUpdate,
    MembreDispoOut,
    PlageOut,
    SemaineDispoOut,
)

router = APIRouter(prefix="/api", tags=["disponibilités"])
DbSession = Annotated[Session, Depends(get_db)]

PONCTUELLE = "ponctuelle"
HEBDO = "hebdo"
RETIREE = "retiree"

MINUTES_JOUR = 24 * 60


# --- Outils -------------------------------------------------------------------


def lundi(jour: date) -> date:
    return jour - timedelta(days=jour.weekday())


def minutes(heure: time, fin: bool = False) -> int:
    """Minutes depuis minuit ; une fin à 23:59 compte jusqu'à minuit."""
    if fin and heure >= FIN_JOURNEE:
        return MINUTES_JOUR
    return heure.hour * 60 + heure.minute


def _hhmm(heure: time) -> str:
    return heure.strftime("%H:%M")


def _occurrences(db: Session, ids_user: list[int], debut: date) -> list[tuple[Disponibilite, date, bool]]:
    """Plages (ponctuelles et planning type) des utilisateurs sur la semaine du lundi `debut`.

    Renvoie (plage, date de l'occurrence, retirée cette semaine ?).
    """
    fin = debut + timedelta(days=6)
    lignes = db.scalars(
        select(Disponibilite).where(
            Disponibilite.id_user.in_(ids_user),
            or_(
                (Disponibilite.statut == PONCTUELLE)
                & (Disponibilite.date_dispo >= debut)
                & (Disponibilite.date_dispo <= fin),
                (Disponibilite.statut == HEBDO)
                & (Disponibilite.date_dispo <= fin)
                & (
                    Disponibilite.date_fin_repet.is_(None)
                    | (Disponibilite.date_fin_repet >= debut)
                ),
                (Disponibilite.statut == RETIREE)
                & (Disponibilite.date_dispo >= debut)
                & (Disponibilite.date_dispo <= fin),
            ),
        )
    ).all()

    retraits = {(l.id_dispo_type, l.date_dispo) for l in lignes if l.statut == RETIREE}
    resultat = []
    for plage in lignes:
        if plage.statut == PONCTUELLE:
            resultat.append((plage, plage.date_dispo, False))
        elif plage.statut == HEBDO:
            jour = debut + timedelta(days=plage.date_dispo.weekday())
            if jour < plage.date_dispo:
                continue
            if plage.date_fin_repet is not None and jour > plage.date_fin_repet:
                continue
            resultat.append((plage, jour, (plage.id_dispo, jour) in retraits))
    resultat.sort(key=lambda o: (o[1], o[0].heure_debut_dispo, o[0].heure_fin_dispo, o[0].id_dispo))
    return resultat


def _semaine_out(db: Session, user: Utilisateur, semaine: date) -> SemaineDispoOut:
    debut = lundi(semaine)
    plages = [
        PlageOut(
            id_dispo=plage.id_dispo,
            date=jour,
            jour=jour.weekday(),
            heure_debut=_hhmm(plage.heure_debut_dispo),
            heure_fin=_hhmm(plage.heure_fin_dispo),
            toute_journee=plage.heure_debut_dispo == DEBUT_JOURNEE
            and plage.heure_fin_dispo >= FIN_JOURNEE,
            recurrente=plage.statut == HEBDO,
            retiree=retiree,
        )
        for plage, jour, retiree in _occurrences(db, [user.id_user], debut)
    ]
    return SemaineDispoOut(semaine=debut, plages=plages)


def _get_plage(db: Session, id_dispo: int, user: Utilisateur) -> Disponibilite:
    plage = db.get(Disponibilite, id_dispo)
    if plage is None or plage.id_user != user.id_user or plage.statut == RETIREE:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Disponibilité introuvable.")
    return plage


def _supprimer_retraits(db: Session, plage: Disponibilite, a_partir_de: date | None = None) -> None:
    condition = [Disponibilite.statut == RETIREE, Disponibilite.id_dispo_type == plage.id_dispo]
    if a_partir_de is not None:
        condition.append(Disponibilite.date_dispo >= a_partir_de)
    db.execute(delete(Disponibilite).where(*condition))


def _date_dans_semaine(plage: Disponibilite, semaine: date) -> date:
    """Date de l'occurrence d'une plage du planning type dans la semaine donnée."""
    jour = lundi(semaine) + timedelta(days=plage.date_dispo.weekday())
    if jour < plage.date_dispo or (plage.date_fin_repet and jour > plage.date_fin_repet):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Cette plage ne fait pas partie de cette semaine."
        )
    return jour


# --- Mes disponibilités ---------------------------------------------------------


@router.get("/disponibilites", response_model=SemaineDispoOut)
def mes_disponibilites(
    user: CurrentUser,
    db: DbSession,
    semaine: Annotated[date | None, Query()] = None,
) -> SemaineDispoOut:
    return _semaine_out(db, user, semaine or date.today())


@router.post(
    "/disponibilites", response_model=SemaineDispoOut, status_code=status.HTTP_201_CREATED
)
def ajouter_disponibilite(
    data: DisponibiliteIn, user: CurrentUser, db: DbSession
) -> SemaineDispoOut:
    debut = lundi(data.semaine)
    for j in data.jours:
        db.add(
            Disponibilite(
                id_user=user.id_user,
                date_dispo=debut + timedelta(days=j),
                heure_debut_dispo=data.heure_debut,
                heure_fin_dispo=data.heure_fin,
                statut=HEBDO if data.repeter else PONCTUELLE,
            )
        )
    db.commit()
    return _semaine_out(db, user, debut)


@router.put("/disponibilites/{id_dispo}", response_model=SemaineDispoOut)
def modifier_disponibilite(
    id_dispo: int, data: DisponibiliteUpdate, user: CurrentUser, db: DbSession
) -> SemaineDispoOut:
    """Modifie une plage. Pour le planning type, la modification vaut à partir de la
    semaine affichée : les semaines précédentes gardent l'ancienne plage."""
    plage = _get_plage(db, id_dispo, user)
    debut = lundi(data.semaine)
    nouvelle_date = debut + timedelta(days=data.jour)

    if plage.statut == PONCTUELLE or plage.date_dispo >= debut:
        if plage.statut == HEBDO:
            _date_dans_semaine(plage, debut)
            # Les retraits déjà posés ne correspondent plus au nouveau jour.
            if nouvelle_date.weekday() != plage.date_dispo.weekday():
                _supprimer_retraits(db, plage)
        plage.date_dispo = nouvelle_date
        plage.heure_debut_dispo = data.heure_debut
        plage.heure_fin_dispo = data.heure_fin
    else:
        # Planning type commencé avant cette semaine : on l'arrête la veille et on
        # crée la nouvelle version à partir de cette semaine.
        _date_dans_semaine(plage, debut)
        nouvelle = Disponibilite(
            id_user=user.id_user,
            date_dispo=nouvelle_date,
            heure_debut_dispo=data.heure_debut,
            heure_fin_dispo=data.heure_fin,
            statut=HEBDO,
            date_fin_repet=plage.date_fin_repet,
        )
        db.add(nouvelle)
        db.flush()
        retraits = db.scalars(
            select(Disponibilite).where(
                Disponibilite.statut == RETIREE,
                Disponibilite.id_dispo_type == plage.id_dispo,
                Disponibilite.date_dispo >= debut,
            )
        ).all()
        for retrait in retraits:
            if retrait.date_dispo.weekday() == nouvelle_date.weekday():
                retrait.id_dispo_type = nouvelle.id_dispo
            else:
                db.delete(retrait)
        plage.date_fin_repet = debut - timedelta(days=1)

    db.commit()
    return _semaine_out(db, user, debut)


@router.delete("/disponibilites/{id_dispo}", response_model=SemaineDispoOut)
def supprimer_disponibilite(
    id_dispo: int,
    user: CurrentUser,
    db: DbSession,
    semaine: Annotated[date, Query()],
) -> SemaineDispoOut:
    """Supprime une plage. Une plage du planning type est retirée à partir de la
    semaine affichée, jamais des semaines précédentes."""
    plage = _get_plage(db, id_dispo, user)
    debut = lundi(semaine)
    if plage.statut == HEBDO and plage.date_dispo < debut:
        plage.date_fin_repet = debut - timedelta(days=1)
        _supprimer_retraits(db, plage, a_partir_de=debut)
    else:
        if plage.statut == HEBDO:
            _supprimer_retraits(db, plage)
        db.delete(plage)
    db.commit()
    return _semaine_out(db, user, debut)


@router.post("/disponibilites/{id_dispo}/retrait", response_model=SemaineDispoOut)
def retirer_cette_semaine(
    id_dispo: int,
    user: CurrentUser,
    db: DbSession,
    semaine: Annotated[date, Query()],
) -> SemaineDispoOut:
    """« Retirer cette semaine » : une plage du planning type est ignorée pour cette semaine."""
    plage = _get_plage(db, id_dispo, user)
    if plage.statut != HEBDO:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Seule une plage du planning type peut être retirée."
        )
    jour = _date_dans_semaine(plage, semaine)
    existe = db.scalar(
        select(Disponibilite.id_dispo).where(
            Disponibilite.statut == RETIREE,
            Disponibilite.id_dispo_type == plage.id_dispo,
            Disponibilite.date_dispo == jour,
        )
    )
    if existe is None:
        db.add(
            Disponibilite(
                id_user=user.id_user,
                date_dispo=jour,
                heure_debut_dispo=plage.heure_debut_dispo,
                heure_fin_dispo=plage.heure_fin_dispo,
                statut=RETIREE,
                id_dispo_type=plage.id_dispo,
            )
        )
        db.commit()
    return _semaine_out(db, user, semaine)


@router.delete("/disponibilites/{id_dispo}/retrait", response_model=SemaineDispoOut)
def remettre_cette_semaine(
    id_dispo: int,
    user: CurrentUser,
    db: DbSession,
    semaine: Annotated[date, Query()],
) -> SemaineDispoOut:
    """Annule « Retirer cette semaine »."""
    plage = _get_plage(db, id_dispo, user)
    debut = lundi(semaine)
    db.execute(
        delete(Disponibilite).where(
            Disponibilite.statut == RETIREE,
            Disponibilite.id_dispo_type == plage.id_dispo,
            Disponibilite.date_dispo >= debut,
            Disponibilite.date_dispo <= debut + timedelta(days=6),
        )
    )
    db.commit()
    return _semaine_out(db, user, debut)


# --- Disponibilités du groupe ---------------------------------------------------


def creneaux_communs(
    intervalles: dict[int, list[tuple[int, int]]],
) -> list[tuple[int, int, list[int]]]:
    """Découpe une journée en créneaux où le même ensemble de membres est libre.

    `intervalles` associe à chaque id_user ses plages (début, fin) en minutes.
    Renvoie (début, fin, membres libres) pour chaque créneau où au moins un membre
    est libre, en fusionnant les créneaux voisins qui ont les mêmes membres.
    """
    bornes = sorted({b for plages in intervalles.values() for p in plages for b in p})
    creneaux: list[tuple[int, int, list[int]]] = []
    for a, b in zip(bornes, bornes[1:]):
        libres = sorted(
            id_user
            for id_user, plages in intervalles.items()
            if any(d <= a and b <= f for d, f in plages)
        )
        if not libres:
            continue
        if creneaux and creneaux[-1][1] == a and creneaux[-1][2] == libres:
            creneaux[-1] = (creneaux[-1][0], b, libres)
        else:
            creneaux.append((a, b, libres))
    return creneaux


@router.get("/groupes/{id_grp}/disponibilites", response_model=DisponibilitesGroupeOut)
def disponibilites_groupe(
    id_grp: int,
    _membership: Membership,
    db: DbSession,
    semaine: Annotated[date | None, Query()] = None,
) -> DisponibilitesGroupeOut:
    debut = lundi(semaine or date.today())
    membres = db.execute(
        select(Utilisateur.id_user, Utilisateur.nom_user)
        .join(UtilisateurGroupe, UtilisateurGroupe.id_user == Utilisateur.id_user)
        .where(UtilisateurGroupe.id_grp == id_grp)
        .order_by(Utilisateur.nom_user, Utilisateur.id_user)
    ).all()
    ids = [m.id_user for m in membres]
    renseignes = set(
        db.scalars(
            select(Disponibilite.id_user)
            .where(
                Disponibilite.id_user.in_(ids),
                Disponibilite.statut.in_((PONCTUELLE, HEBDO)),
            )
            .distinct()
        )
    )

    par_jour: dict[date, dict[int, list[tuple[int, int]]]] = {}
    for plage, jour, retiree in _occurrences(db, ids, debut):
        if retiree:
            continue
        par_jour.setdefault(jour, {}).setdefault(plage.id_user, []).append(
            (minutes(plage.heure_debut_dispo), minutes(plage.heure_fin_dispo, fin=True))
        )

    creneaux = [
        CreneauGroupeOut(date=jour, jour=jour.weekday(), debut=a, fin=b, disponibles=libres)
        for jour in sorted(par_jour)
        for a, b, libres in creneaux_communs(par_jour[jour])
    ]
    return DisponibilitesGroupeOut(
        semaine=debut,
        membres=[
            MembreDispoOut(id_user=m.id_user, nom_user=m.nom_user, renseigne=m.id_user in renseignes)
            for m in membres
        ],
        creneaux=creneaux,
    )
