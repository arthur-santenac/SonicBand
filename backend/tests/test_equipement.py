from backend.models import Equipement


def test_equipement_table_name():
    assert Equipement.__tablename__ == "equipement"


def test_equipement_columns():
    assert set(Equipement.__table__.columns.keys()) == {
        "id_equipement",
        "nom_equipement",
        "cat_equipement",
    }
