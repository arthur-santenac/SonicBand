"""Rôles admin / membre : création, promotion, rétrogradation et retrait."""

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
from backend.migrations import mettre_a_jour_schema
from backend.models import Base, Groupe, Utilisateur, UtilisateurGroupe


@pytest.fixture
def ctx(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        users = [
            Utilisateur(nom_user=nom, email_user=f"{nom.lower()}@example.test", mdp_hash="h")
            for nom in ("Paul", "Arthur", "Louis")
        ]
        db.add_all(users)
        db.commit()
        ids = {u.nom_user: u.id_user for u in users}

    courant = {"id": ids["Paul"]}

    def override_db():
        with Session(engine) as db:
            yield db

    monkeypatch.setattr(backend.database, "engine", engine)
    monkeypatch.setattr(backend.main, "get_settings", lambda: Settings(database_url="sqlite://"))
    backend.main.app.dependency_overrides[get_db] = override_db
    backend.main.app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id_user=courant["id"]
    )
    with TestClient(backend.main.app) as client:
        groupe = client.post("/api/groupes", json={"nom": "Nirvana"}).json()
        with Session(engine) as db:
            for nom in ("Arthur", "Louis"):
                db.add(UtilisateurGroupe(id_user=ids[nom], id_grp=groupe["id_grp"], role="membre"))
            db.commit()
        yield SimpleNamespace(
            client=client, ids=ids, courant=courant, id_grp=groupe["id_grp"], groupe=groupe,
            engine=engine,
        )
    backend.main.app.dependency_overrides.clear()
    engine.dispose()


def _roles(ctx):
    data = ctx.client.get(f"/api/groupes/{ctx.id_grp}/membres").json()
    return {m["nom_user"]: m["role"] for m in data["membres"]}


def test_le_createur_est_admin(ctx):
    assert ctx.groupe["mon_role"] == "admin"
    assert _roles(ctx) == {"Paul": "admin", "Arthur": "membre", "Louis": "membre"}


def test_un_admin_peut_nommer_un_membre_admin(ctx):
    r = ctx.client.patch(
        f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Arthur']}", json={"role": "admin"}
    )
    assert r.status_code == 200
    assert r.json()["role"] == "admin"
    assert _roles(ctx)["Arthur"] == "admin"

    # Le nouvel admin peut à son tour inviter et nommer.
    ctx.courant["id"] = ctx.ids["Arthur"]
    assert ctx.client.post(
        f"/api/groupes/{ctx.id_grp}/invitations", json={"email": "kurt@example.com"}
    ).status_code == 201
    assert ctx.client.patch(
        f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Louis']}", json={"role": "admin"}
    ).status_code == 200


def test_un_membre_ne_peut_pas_changer_les_roles(ctx):
    ctx.courant["id"] = ctx.ids["Arthur"]
    r = ctx.client.patch(
        f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Arthur']}", json={"role": "admin"}
    )
    assert r.status_code == 403


def test_role_inconnu_refuse(ctx):
    r = ctx.client.patch(
        f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Arthur']}", json={"role": "super_admin"}
    )
    assert r.status_code == 422


def test_le_groupe_garde_au_moins_un_admin(ctx):
    r = ctx.client.patch(
        f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Paul']}", json={"role": "membre"}
    )
    assert r.status_code == 409

    ctx.client.patch(f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Arthur']}", json={"role": "admin"})
    r = ctx.client.patch(
        f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Paul']}", json={"role": "membre"}
    )
    assert r.status_code == 200
    assert _roles(ctx)["Paul"] == "membre"


def test_un_admin_retire_un_autre_admin_mais_pas_lui_meme(ctx):
    ctx.client.patch(f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Arthur']}", json={"role": "admin"})
    assert ctx.client.delete(
        f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Paul']}"
    ).status_code == 403
    assert ctx.client.delete(
        f"/api/groupes/{ctx.id_grp}/membres/{ctx.ids['Arthur']}"
    ).status_code == 204
    assert "Arthur" not in _roles(ctx)


def test_migration_convertit_super_admin_en_admin(ctx):
    with ctx.engine.begin() as conn:
        conn.execute(
            text("UPDATE utilisateur_groupe SET role = 'super_admin' WHERE id_user = :id"),
            {"id": ctx.ids["Paul"]},
        )
    mettre_a_jour_schema(ctx.engine)
    assert _roles(ctx)["Paul"] == "admin"
