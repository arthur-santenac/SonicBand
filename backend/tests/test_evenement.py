from backend.models import Evenement


def test_evenement_table_name():
    assert Evenement.__tablename__ == "evenement"


def test_evenement_columns():
    assert set(Evenement.__table__.columns.keys()) == {
        "id_event",
        "titre_event",
        "type",
        "date_event",
        "heure_debut_event",
        "heure_fin_event",
        "lieu_event",
        "id_rep",
    }
