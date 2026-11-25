"""Mises à jour légères du schéma d'une base déjà créée.

`create_all` (SQLite) et `database/init.sql` (PostgreSQL) ne créent les tables que
si elles n'existent pas : une base créée avant l'ajout d'une colonne ne la reçoit
pas. On ajoute ici au démarrage les tables et colonnes manquantes, sans rien effacer.

On convertit aussi l'ancien rôle « super_admin » en « admin » : il n'y a plus
que deux rôles (admin et membre) et un groupe peut avoir plusieurs admins.
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# Tables apparues après la première version de la base.
TABLES_AJOUTEES = ("piece_jointe",)

# table -> [(colonne, définition SQL valable pour SQLite et PostgreSQL)]
COLONNES_AJOUTEES = {
    "disponibilite": [
        ("date_fin_repet", "DATE"),
        (
            "id_dispo_type",
            "INTEGER REFERENCES disponibilite(id_dispo) ON DELETE CASCADE",
        ),
    ],
}


def mettre_a_jour_schema(engine: Engine) -> None:
    from backend.models import Base

    # On lit tout le schéma avant d'ouvrir la transaction d'écriture : l'inspecteur
    # peut réutiliser la même connexion et annuler ce qui y a été fait.
    inspecteur = inspect(engine)
    tables = set(inspecteur.get_table_names())
    colonnes_existantes = {
        table: {c["name"] for c in inspecteur.get_columns(table)}
        for table in COLONNES_AJOUTEES
        if table in tables
    }

    for nom in TABLES_AJOUTEES:
        if nom not in tables:
            Base.metadata.tables[nom].create(engine, checkfirst=True)

    with engine.begin() as conn:
        for table, existantes in colonnes_existantes.items():
            for nom, definition in COLONNES_AJOUTEES[table]:
                if nom not in existantes:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {nom} {definition}"))
        if "utilisateur_groupe" in tables:
            conn.execute(text("DROP INDEX IF EXISTS utilisateur_groupe_un_super_admin"))
            conn.execute(
                text("UPDATE utilisateur_groupe SET role = 'admin' WHERE role = 'super_admin'")
            )
