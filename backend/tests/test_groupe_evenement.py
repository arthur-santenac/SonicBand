from backend.models import GroupeEvenement


def test_groupe_evenement_table_name():
    assert GroupeEvenement.__tablename__ == "groupe_evenement"


def test_groupe_evenement_columns():
    assert set(GroupeEvenement.__table__.columns.keys()) == {
        "id_grp",
        "id_event",
    }
