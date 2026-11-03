from backend.models import Morceau


def test_morceau_table_name():
    assert Morceau.__tablename__ == "morceau"


def test_morceau_columns():
    assert set(Morceau.__table__.columns.keys()) == {
        "id_song",
        "titre_song",
        "compositeur",
        "lien_youtube",
        "url_img",
        "date_crea_song",
    }
