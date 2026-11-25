from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import backend.database
import backend.main
from backend.auth import get_current_user
from backend.config import Settings
from backend.database import get_db
from backend.disponibilites import creneaux_communs
from backend.migrations import mettre_a_jour_schema
from backend.models import Base, Groupe, Utilisateur, UtilisateurGroupe

# Semaine du lundi 9 au dimanche 15 novembre 2026 (celle de la maquette).
SEMAINE = "2026-11-09"
SEMAINE_SUIVANTE = "2026-11-16"
SEMAINE_PRECEDENTE = "2026-11-02"


@pytest.fixture
def dispo_client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        paul = Utilisateur(nom_user="Paul", email_user="paul@example.test", mdp_hash="h")
        arthur = Utilisateur(nom_user="Arthur", email_user="arthur@example.test", mdp_hash="h")
        louis = Utilisateur(nom_user="Louis", email_user="louis@example.test", mdp_hash="h")
        dehors = Utilisateur(nom_user="Dehors", email_user="dehors@example.test", mdp_hash="h")
        nirvana = Groupe(nom_grp="Nirvana")
        u2 = Groupe(nom_grp="U2")
        db.add_all([paul, arthur, louis, dehors, nirvana, u2])
        db.flush()
        db.add_all(
            [
                UtilisateurGroupe(id_user=paul.id_user, id_grp=nirvana.id_grp, role="super_admin"),
                UtilisateurGroupe(id_user=arthur.id_user, id_grp=nirvana.id_grp, role="membre"),
                UtilisateurGroupe(id_user=louis.id_user, id_grp=nirvana.id_grp, role="membre"),
                UtilisateurGroupe(id_user=paul.id_user, id_grp=u2.id_grp, role="membre"),
                UtilisateurGroupe(id_user=dehors.id_user, id_grp=u2.id_grp, role="super_admin"),
            ]
        )
        db.commit()
        ids = SimpleNamespace(
            paul=paul.id_user,
            arthur=arthur.id_user,
            louis=louis.id_user,
            dehors=dehors.id_user,
            nirvana=nirvana.id_grp,
            u2=u2.id_grp,
        )

    current = {"id_user": ids.paul}

    def override_db():
        with Session(engine) as db:
            yield db

    def override_user():
        return SimpleNamespace(id_user=current["id_user"])

    monkeypatch.setattr(backend.database, "engine", engine)
    monkeypatch.setattr(backend.main, "get_settings", lambda: Settings(database_url="sqlite://"))
    backend.main.app.dependency_overrides[get_db] = override_db
    backend.main.app.dependency_overrides[get_current_user] = override_user

    def en_tant_que(id_user):
        current["id_user"] = id_user

    with TestClient(backend.main.app) as client:
        yield client, ids, en_tant_que
    backend.main.app.dependency_overrides.clear()
    engine.dispose()


def ajouter(client, **kwargs):
    body = {"semaine": SEMAINE, "jours": [0], "heure_debut": "19:00", "heure_fin": "22:00"}
    body.update(kwargs)
    response = client.post("/api/disponibilites", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def plages(client, semaine=SEMAINE):
    response = client.get("/api/disponibilites", params={"semaine": semaine})
    assert response.status_code == 200, response.text
    return response.json()["plages"]


def test_ajout_ponctuel_sur_plusieurs_jours_uniquement_cette_semaine(dispo_client):
    client, _, _ = dispo_client

    semaine = ajouter(client, jours=[0, 1], heure_debut="19:30", heure_fin="22:30")

    assert semaine["semaine"] == SEMAINE
    assert [(p["date"], p["heure_debut"], p["heure_fin"]) for p in semaine["plages"]] == [
        ("2026-11-09", "19:30", "22:30"),
        ("2026-11-10", "19:30", "22:30"),
    ]
    assert all(not p["recurrente"] for p in semaine["plages"])
    assert plages(client, SEMAINE_SUIVANTE) == []


def test_un_jour_de_la_semaine_suffit_pour_designer_la_semaine(dispo_client):
    client, _, _ = dispo_client
    ajouter(client, semaine="2026-11-12", jours=[6])
    assert [p["date"] for p in plages(client)] == ["2026-11-15"]


def test_planning_type_revient_chaque_semaine_mais_pas_avant(dispo_client):
    client, _, _ = dispo_client
    ajouter(client, jours=[1], repeter=True)

    for semaine, date_attendue in [(SEMAINE, "2026-11-10"), (SEMAINE_SUIVANTE, "2026-11-17")]:
        [plage] = plages(client, semaine)
        assert plage["date"] == date_attendue
        assert plage["recurrente"] is True
    assert plages(client, SEMAINE_PRECEDENTE) == []


def test_toute_la_journee(dispo_client):
    client, _, _ = dispo_client
    [plage] = ajouter(client, toute_journee=True, heure_debut=None, heure_fin=None)["plages"]
    assert (plage["heure_debut"], plage["heure_fin"], plage["toute_journee"]) == (
        "00:00",
        "23:59",
        True,
    )


@pytest.mark.parametrize(
    "body",
    [
        {"heure_debut": "22:00", "heure_fin": "19:00"},
        {"heure_debut": "19:00", "heure_fin": "19:00"},
        {"heure_debut": None},
        {"jours": []},
        {"jours": [7]},
    ],
)
def test_ajout_invalide(dispo_client, body):
    client, _, _ = dispo_client
    payload = {"semaine": SEMAINE, "jours": [0], "heure_debut": "19:00", "heure_fin": "22:00"}
    payload.update(body)
    assert client.post("/api/disponibilites", json=payload).status_code == 422


def test_retirer_puis_remettre_une_plage_du_planning_type(dispo_client):
    client, _, _ = dispo_client
    [plage] = ajouter(client, jours=[1], repeter=True)["plages"]

    response = client.post(
        f"/api/disponibilites/{plage['id_dispo']}/retrait", params={"semaine": SEMAINE}
    )
    assert response.status_code == 200
    assert response.json()["plages"][0]["retiree"] is True
    # Les autres semaines ne sont pas touchées.
    assert plages(client, SEMAINE_SUIVANTE)[0]["retiree"] is False

    response = client.delete(
        f"/api/disponibilites/{plage['id_dispo']}/retrait", params={"semaine": SEMAINE}
    )
    assert response.json()["plages"][0]["retiree"] is False


def test_une_plage_ponctuelle_ne_peut_pas_etre_retiree(dispo_client):
    client, _, _ = dispo_client
    [plage] = ajouter(client)["plages"]
    response = client.post(
        f"/api/disponibilites/{plage['id_dispo']}/retrait", params={"semaine": SEMAINE}
    )
    assert response.status_code == 400


def test_supprimer_planning_type_a_partir_de_la_semaine_affichee(dispo_client):
    client, _, _ = dispo_client
    [plage] = ajouter(client, jours=[1], repeter=True)["plages"]

    response = client.delete(
        f"/api/disponibilites/{plage['id_dispo']}", params={"semaine": SEMAINE_SUIVANTE}
    )
    assert response.status_code == 200
    assert response.json()["plages"] == []
    assert plages(client, "2026-11-23") == []
    # La semaine précédente garde la plage.
    assert len(plages(client, SEMAINE)) == 1


def test_supprimer_planning_type_des_sa_premiere_semaine_le_supprime(dispo_client):
    client, _, _ = dispo_client
    [plage] = ajouter(client, jours=[1], repeter=True)["plages"]
    client.post(f"/api/disponibilites/{plage['id_dispo']}/retrait", params={"semaine": SEMAINE})

    client.delete(f"/api/disponibilites/{plage['id_dispo']}", params={"semaine": SEMAINE})
    assert plages(client) == []
    assert plages(client, SEMAINE_SUIVANTE) == []


def test_modifier_une_plage_ponctuelle(dispo_client):
    client, _, _ = dispo_client
    [plage] = ajouter(client)["plages"]

    response = client.put(
        f"/api/disponibilites/{plage['id_dispo']}",
        json={"semaine": SEMAINE, "jour": 3, "heure_debut": "12:00", "heure_fin": "16:00"},
    )
    assert response.status_code == 200
    [modifiee] = response.json()["plages"]
    assert (modifiee["date"], modifiee["heure_debut"], modifiee["heure_fin"]) == (
        "2026-11-12",
        "12:00",
        "16:00",
    )


def test_modifier_planning_type_ne_change_pas_les_semaines_precedentes(dispo_client):
    client, _, _ = dispo_client
    [plage] = ajouter(client, jours=[1], repeter=True)["plages"]

    response = client.put(
        f"/api/disponibilites/{plage['id_dispo']}",
        json={
            "semaine": SEMAINE_SUIVANTE,
            "jour": 2,
            "heure_debut": "18:00",
            "heure_fin": "21:00",
        },
    )
    assert response.status_code == 200
    [nouvelle] = response.json()["plages"]
    assert (nouvelle["date"], nouvelle["heure_debut"], nouvelle["recurrente"]) == (
        "2026-11-18",
        "18:00",
        True,
    )
    [ancienne] = plages(client, SEMAINE)
    assert (ancienne["date"], ancienne["heure_debut"]) == ("2026-11-10", "19:00")
    [plus_tard] = plages(client, "2026-11-23")
    assert (plus_tard["date"], plus_tard["heure_debut"]) == ("2026-11-25", "18:00")


def test_on_ne_touche_pas_aux_plages_des_autres(dispo_client):
    client, ids, en_tant_que = dispo_client
    [plage] = ajouter(client)["plages"]

    en_tant_que(ids.arthur)
    assert plages(client) == []
    response = client.delete(f"/api/disponibilites/{plage['id_dispo']}", params={"semaine": SEMAINE})
    assert response.status_code == 404
    response = client.put(
        f"/api/disponibilites/{plage['id_dispo']}",
        json={"semaine": SEMAINE, "jour": 0, "heure_debut": "08:00", "heure_fin": "09:00"},
    )
    assert response.status_code == 404


def test_memes_disponibilites_dans_tous_les_groupes(dispo_client):
    client, ids, _ = dispo_client
    ajouter(client, jours=[4], heure_debut="19:00", heure_fin="22:00")

    for id_grp in (ids.nirvana, ids.u2):
        data = client.get(
            f"/api/groupes/{id_grp}/disponibilites", params={"semaine": SEMAINE}
        ).json()
        assert data["creneaux"] == [
            {
                "date": "2026-11-13",
                "jour": 4,
                "debut": 19 * 60,
                "fin": 22 * 60,
                "disponibles": [ids.paul],
            }
        ]


def test_heat_map_du_groupe_compte_les_membres_libres(dispo_client):
    client, ids, en_tant_que = dispo_client
    ajouter(client, jours=[0], heure_debut="18:00", heure_fin="22:00", repeter=True)
    en_tant_que(ids.arthur)
    ajouter(client, jours=[0], heure_debut="19:00", heure_fin="23:00")
    # Une plage retirée cette semaine ne compte pas.
    [plage] = ajouter(client, jours=[2], heure_debut="10:00", heure_fin="12:00", repeter=True)[
        "plages"
    ][1:]
    client.post(f"/api/disponibilites/{plage['id_dispo']}/retrait", params={"semaine": SEMAINE})

    data = client.get(f"/api/groupes/{ids.nirvana}/disponibilites", params={"semaine": SEMAINE})
    assert data.status_code == 200
    data = data.json()

    assert data["semaine"] == SEMAINE
    assert [(m["nom_user"], m["renseigne"]) for m in data["membres"]] == [
        ("Arthur", True),
        ("Louis", False),
        ("Paul", True),
    ]
    assert [(c["date"], c["debut"], c["fin"], c["disponibles"]) for c in data["creneaux"]] == [
        ("2026-11-09", 18 * 60, 19 * 60, [ids.paul]),
        ("2026-11-09", 19 * 60, 22 * 60, sorted([ids.paul, ids.arthur])),
        ("2026-11-09", 22 * 60, 23 * 60, [ids.arthur]),
    ]


def test_disponibilites_du_groupe_reservees_aux_membres(dispo_client):
    client, ids, en_tant_que = dispo_client
    en_tant_que(ids.dehors)
    response = client.get(f"/api/groupes/{ids.nirvana}/disponibilites")
    assert response.status_code == 404


def test_creneaux_communs_fusionne_et_gere_minuit():
    assert creneaux_communs({1: [(0, 600), (600, 1440)], 2: [(1380, 1440)]}) == [
        (0, 1380, [1]),
        (1380, 1440, [1, 2]),
    ]
    assert creneaux_communs({}) == []


def test_migration_ajoute_les_colonnes_manquantes():
    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE disponibilite (id_dispo INTEGER PRIMARY KEY, date_dispo DATE, "
                "heure_debut_dispo TIME, heure_fin_dispo TIME, statut VARCHAR(50), id_user INT)"
            )
        )
    mettre_a_jour_schema(engine)
    mettre_a_jour_schema(engine)  # sans effet la deuxième fois
    with engine.connect() as conn:
        colonnes = {row[1] for row in conn.execute(text("PRAGMA table_info(disponibilite)"))}
    assert {"date_fin_repet", "id_dispo_type"} <= colonnes
