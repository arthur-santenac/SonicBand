from backend.models import Repertoire


def test_repertoire_table_name():
    assert Repertoire.__tablename__ == "repertoire"


def test_repertoire_columns():
    assert set(Repertoire.__table__.columns.keys()) == {
        "id_rep",
        "nom_rep",
        "id_grp",
    }
