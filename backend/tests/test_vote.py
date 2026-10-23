from backend.models import Vote


def test_vote_table_name():
    assert Vote.__tablename__ == "vote"


def test_vote_columns():
    assert set(Vote.__table__.columns.keys()) == {
        "id_vote",
        "note",
        "id_user",
        "id_song",
    }
