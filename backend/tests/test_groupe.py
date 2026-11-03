from backend.models import Groupe


def test_groupe_table_name():
    assert Groupe.__tablename__ == "groupe"


def test_groupe_columns():
    assert set(Groupe.__table__.columns.keys()) == {
        "id_grp",
        "nom_grp",
        "description_grp",
        "url_photo",
        "date_crea_grp",
    }
