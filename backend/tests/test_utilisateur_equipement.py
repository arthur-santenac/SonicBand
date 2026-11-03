from backend.models import UtilisateurEquipement


def test_utilisateur_equipement_table_name():
    assert UtilisateurEquipement.__tablename__ == "utilisateur_equipement"


def test_utilisateur_equipement_columns():
    assert set(UtilisateurEquipement.__table__.columns.keys()) == {
        "id_user",
        "id_equipement",
    }
