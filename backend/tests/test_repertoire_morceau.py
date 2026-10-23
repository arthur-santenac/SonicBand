from backend.models import RepertoireMorceau


def test_repertoire_morceau_table_name():
    assert RepertoireMorceau.__tablename__ == "repertoire_morceau"


def test_repertoire_morceau_columns():
    assert set(RepertoireMorceau.__table__.columns.keys()) == {
        "id_rep",
        "id_song",
        "position",
    }
