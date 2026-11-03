from backend.models import Disponibilite


def test_disponibilite_table_name():
    assert Disponibilite.__tablename__ == "disponibilite"


def test_disponibilite_columns():
    assert set(Disponibilite.__table__.columns.keys()) == {
        "id_dispo",
        "date_dispo",
        "heure_debut_dispo",
        "heure_fin_dispo",
        "statut",
        "id_user",
    }
