from backend.models import UtilisateurGroupe


def test_utilisateur_groupe_table_name():
    assert UtilisateurGroupe.__tablename__ == "utilisateur_groupe"


def test_utilisateur_groupe_columns():
    assert set(UtilisateurGroupe.__table__.columns.keys()) == {
        "id_user",
        "id_grp",
        "role",
        "date_rejoint",
    }
