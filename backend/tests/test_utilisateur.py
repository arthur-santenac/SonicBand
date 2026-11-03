from backend.models import Utilisateur


def test_utilisateur_table_name():
    assert Utilisateur.__tablename__ == "utilisateur"


def test_utilisateur_columns():
    assert set(Utilisateur.__table__.columns.keys()) == {
        "id_user",
        "nom_user",
        "email_user",
        "mdp_hash",
        "date_crea_user",
    }
