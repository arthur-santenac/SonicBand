from backend.models import GroupeEquipement


def test_groupe_equipement_table_name():
    assert GroupeEquipement.__tablename__ == "groupe_equipement"


def test_groupe_equipement_columns():
    assert set(GroupeEquipement.__table__.columns.keys()) == {
        "id_grp",
        "id_equipement",
    }
