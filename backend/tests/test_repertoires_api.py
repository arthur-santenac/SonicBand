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
def repertoire_client(monkeypatch):
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

    current_user = {"id_user": None}

    def override_db():
        with Session(engine) as db:
            yield db

    def override_user():
        return SimpleNamespace(id_user=current_user["id_user"])

    with Session(engine) as db:
        current_user["id_user"] = user_id
        outsider = Utilisateur(
            nom_user="Autre",
            email_user="autre@example.test",
            mdp_hash="hash",
        )
        db.add(outsider)
        db.commit()
        outsider_id = outsider.id_user

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


def test_group_members_can_manage_repertoires_and_songs(repertoire_client):
    client, group_id, _, _, _ = repertoire_client

    create_response = client.post(
        f"/api/groupes/{group_id}/repertoires",
        json={"nom_rep": "Setlist"},
    )
    assert create_response.status_code == 201
    repertoire = create_response.json()
    assert repertoire["nom_rep"] == "Setlist"
    assert repertoire["morceaux"] == []

    song_response = client.post(
        f"/api/groupes/{group_id}/repertoires/{repertoire['id_rep']}/morceaux",
        json={
            "titre_song": "Come Together",
            "compositeur": "The Beatles",
            "lien_youtube": "https://youtube.com/watch?v=example",
        },
    )
    assert song_response.status_code == 201
    song = song_response.json()
    assert song["position"] == 1
    assert song["lien_youtube"] == "https://youtube.com/watch?v=example"

    listed = client.get(f"/api/groupes/{group_id}/repertoires")
    assert listed.status_code == 200
    assert listed.json()[0]["morceaux"][0]["titre_song"] == "Come Together"

    delete_response = client.delete(
        f"/api/groupes/{group_id}/repertoires/{repertoire['id_rep']}"
        f"/morceaux/{song['id_song']}"
    )
    assert delete_response.status_code == 204
    assert client.get(f"/api/groupes/{group_id}/repertoires").json()[0]["morceaux"] == []


def test_repertoire_routes_are_limited_to_group_members(repertoire_client):
    client, group_id, current_user, engine, outsider_id = repertoire_client
    current_user["id_user"] = outsider_id

    response = client.get(f"/api/groupes/{group_id}/repertoires")
    assert response.status_code == 404


def test_repertoire_names_cannot_be_blank(repertoire_client):
    client, group_id, _, _, _ = repertoire_client
    response = client.post(
        f"/api/groupes/{group_id}/repertoires",
        json={"nom_rep": "   "},
    )
    assert response.status_code == 422
