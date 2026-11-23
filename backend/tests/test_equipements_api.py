from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import backend.database
import backend.main
from backend.auth import get_current_user
from backend.config import Settings
from backend.database import get_db
from backend.models import Base, Groupe, Utilisateur, UtilisateurGroupe


@pytest.fixture
def equipement_client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = Utilisateur(
            nom_user="Membre",
            email_user="membre@example.test",
            mdp_hash="hash",
        )
        groupe = Groupe(nom_grp="Sonic Band")
        db.add_all([user, groupe])
        db.flush()
        db.add(
            UtilisateurGroupe(
                id_user=user.id_user,
                id_grp=groupe.id_grp,
                role="super_admin",
            )
        )
        db.commit()
        user_id, group_id = user.id_user, groupe.id_grp

        outsider = Utilisateur(
            nom_user="Autre",
            email_user="autre@example.test",
            mdp_hash="hash",
        )
        db.add(outsider)
        db.commit()
        outsider_id = outsider.id_user

    current_user = {"id_user": user_id}

    def override_db():
        with Session(engine) as db:
            yield db

    def override_user():
        return SimpleNamespace(id_user=current_user["id_user"])

    monkeypatch.setattr(backend.database, "engine", engine)
    monkeypatch.setattr(
        backend.main, "get_settings", lambda: Settings(database_url="sqlite://")
    )
    backend.main.app.dependency_overrides[get_db] = override_db
    backend.main.app.dependency_overrides[get_current_user] = override_user
    with TestClient(backend.main.app) as client:
        yield client, group_id, current_user, engine, outsider_id
    backend.main.app.dependency_overrides.clear()
    engine.dispose()


def test_personal_and_group_equipment_can_be_managed(equipement_client):
    client, group_id, _, _, _ = equipement_client

    personal_response = client.post(
        "/api/equipements/personnels",
        json={"nom_equipement": "Guitare"},
    )
    assert personal_response.status_code == 201
    personal = personal_response.json()
    assert personal["nom_equipement"] == "Guitare"
    assert personal["est_equipement_groupe"] is False

    group_list = client.get(f"/api/groupes/{group_id}/equipements")
    assert group_list.status_code == 200
    assert group_list.json() == [
        {
            "id_equipement": personal["id_equipement"],
            "nom_equipement": "Guitare",
            "proprietaire": "Membre",
            "est_equipement_groupe": False,
        }
    ]

    group_response = client.post(
        f"/api/groupes/{group_id}/equipements",
        json={"nom_equipement": "Table de mixage"},
    )
    assert group_response.status_code == 201
    group_equipment = group_response.json()
    assert group_equipment["proprietaire"] == "Sonic Band"
    assert group_equipment["est_equipement_groupe"] is True

    personal_list = client.get("/api/equipements/personnels")
    assert [item["id_equipement"] for item in personal_list.json()] == [
        personal["id_equipement"]
    ]
    assert len(client.get(f"/api/groupes/{group_id}/equipements").json()) == 2

    remove_group = client.delete(
        f"/api/groupes/{group_id}/equipements/{group_equipment['id_equipement']}"
    )
    assert remove_group.status_code == 204
    assert len(client.get(f"/api/groupes/{group_id}/equipements").json()) == 1

    remove_personal = client.delete(
        f"/api/equipements/personnels/{personal['id_equipement']}"
    )
    assert remove_personal.status_code == 204
    assert client.get("/api/equipements/personnels").json() == []
    assert client.get(f"/api/groupes/{group_id}/equipements").json() == []


def test_equipment_routes_require_group_membership_and_personal_ownership(
    equipement_client,
):
    client, group_id, current_user, _, outsider_id = equipement_client
    created = client.post(
        "/api/equipements/personnels",
        json={"nom_equipement": "Micro"},
    ).json()

    current_user["id_user"] = outsider_id
    assert client.get(f"/api/groupes/{group_id}/equipements").status_code == 404
    response = client.delete(
        f"/api/equipements/personnels/{created['id_equipement']}"
    )
    assert response.status_code == 404


def test_equipment_names_cannot_be_blank(equipement_client):
    client, group_id, _, _, _ = equipement_client
    assert (
        client.post(
            f"/api/groupes/{group_id}/equipements",
            json={"nom_equipement": "  "},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/equipements/personnels",
            json={"nom_equipement": "  "},
        ).status_code
        == 422
    )
