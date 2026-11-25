"""Pièces jointes des morceaux : ajout, téléchargement, suppression et droits."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import backend.database
import backend.main
import backend.repertoires
from backend.auth import get_current_user
from backend.config import Settings
from backend.database import get_db
from backend.models import Base, PieceJointe, Utilisateur


@pytest.fixture
def ctx(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        paul = Utilisateur(nom_user="Paul", email_user="paul@example.test", mdp_hash="h")
        dehors = Utilisateur(nom_user="Dehors", email_user="dehors@example.test", mdp_hash="h")
        db.add_all([paul, dehors])
        db.commit()
        ids = {"paul": paul.id_user, "dehors": dehors.id_user}

    courant = {"id": ids["paul"]}

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
        g = client.post("/api/groupes", json={"nom": "Nirvana"}).json()["id_grp"]
        rep = client.post(f"/api/groupes/{g}/repertoires", json={"nom_rep": "Concert"}).json()
        song = client.post(
            f"/api/groupes/{g}/repertoires/{rep['id_rep']}/morceaux",
            json={"titre_song": "Lithium", "compositeur": "Nirvana"},
        ).json()
        base = f"/api/groupes/{g}/repertoires/{rep['id_rep']}/morceaux/{song['id_song']}"
        yield SimpleNamespace(
            client=client, ids=ids, courant=courant, g=g, rep=rep["id_rep"], song=song,
            base=base, engine=engine,
        )
    backend.main.app.dependency_overrides.clear()
    engine.dispose()


def _envoyer(ctx, *fichiers):
    return ctx.client.post(
        f"{ctx.base}/pieces-jointes",
        files=[("fichiers", f) for f in fichiers],
    )


def test_un_nouveau_morceau_na_pas_de_piece_jointe(ctx):
    assert ctx.song["pieces_jointes"] == []


def test_ajouter_lister_telecharger_supprimer(ctx):
    r = _envoyer(
        ctx,
        ("partition.pdf", b"%PDF-1.4 contenu", "application/pdf"),
        ("maquette.mp3", b"ID3audio", "audio/mpeg"),
    )
    assert r.status_code == 201, r.text
    pieces = r.json()
    assert [p["nom_fichier"] for p in pieces] == ["partition.pdf", "maquette.mp3"]
    assert pieces[0]["taille"] == len(b"%PDF-1.4 contenu")
    assert "contenu" not in pieces[0]

    reps = ctx.client.get(f"/api/groupes/{ctx.g}/repertoires").json()
    assert [p["nom_fichier"] for p in reps[0]["morceaux"][0]["pieces_jointes"]] == [
        "partition.pdf",
        "maquette.mp3",
    ]

    dl = ctx.client.get(f"{ctx.base}/pieces-jointes/{pieces[0]['id_pj']}")
    assert dl.status_code == 200
    assert dl.content == b"%PDF-1.4 contenu"
    assert dl.headers["content-type"].startswith("application/pdf")
    assert "partition.pdf" in dl.headers["content-disposition"]

    assert ctx.client.delete(f"{ctx.base}/pieces-jointes/{pieces[0]['id_pj']}").status_code == 204
    assert ctx.client.get(f"{ctx.base}/pieces-jointes/{pieces[0]['id_pj']}").status_code == 404


def test_nom_avec_accents_et_chemin(ctx):
    r = _envoyer(ctx, ("C:\\Users\\moi\\Paroles été.txt", b"la la", "text/plain"))
    assert r.json()[0]["nom_fichier"] == "Paroles été.txt"
    dl = ctx.client.get(f"{ctx.base}/pieces-jointes/{r.json()[0]['id_pj']}")
    assert "Paroles%20%C3%A9t%C3%A9.txt" in dl.headers["content-disposition"]


def test_fichier_trop_gros_ou_vide(ctx, monkeypatch):
    monkeypatch.setattr(backend.repertoires, "TAILLE_MAX_PJ", 10)
    assert _envoyer(ctx, ("gros.bin", b"x" * 11, "application/octet-stream")).status_code == 413
    assert _envoyer(ctx, ("vide.txt", b"", "text/plain")).status_code == 400
    with Session(ctx.engine) as db:
        assert db.scalar(select(func.count()).select_from(PieceJointe)) == 0


def test_nombre_maximal(ctx, monkeypatch):
    monkeypatch.setattr(backend.repertoires, "NB_MAX_PJ", 2)
    assert _envoyer(ctx, ("a.txt", b"a", "text/plain"), ("b.txt", b"b", "text/plain")).status_code == 201
    assert _envoyer(ctx, ("c.txt", b"c", "text/plain")).status_code == 400


def test_un_non_membre_ny_a_pas_acces(ctx):
    pj = _envoyer(ctx, ("a.txt", b"a", "text/plain")).json()[0]
    ctx.courant["id"] = ctx.ids["dehors"]
    assert ctx.client.get(f"{ctx.base}/pieces-jointes/{pj['id_pj']}").status_code == 404
    assert _envoyer(ctx, ("b.txt", b"b", "text/plain")).status_code == 404
    assert ctx.client.delete(f"{ctx.base}/pieces-jointes/{pj['id_pj']}").status_code == 404


def test_retirer_le_morceau_supprime_ses_pieces_jointes(ctx):
    _envoyer(ctx, ("a.txt", b"a", "text/plain"))
    r = ctx.client.delete(f"/api/groupes/{ctx.g}/repertoires/{ctx.rep}/morceaux/{ctx.song['id_song']}")
    assert r.status_code == 204
    with Session(ctx.engine) as db:
        assert db.scalar(select(func.count()).select_from(PieceJointe)) == 0
