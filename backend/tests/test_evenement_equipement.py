from backend.models import EvenementEquipement


def test_evenement_equipement_table_name():
    assert EvenementEquipement.__tablename__ == "evenement_equipement"


def test_evenement_equipement_columns():
    assert set(EvenementEquipement.__table__.columns.keys()) == {
        "id_event",
        "id_equipement",
    }
