"""Mises à jour légères du schéma d'une base déjà créée.

`create_all` (SQLite) et `database/init.sql` (PostgreSQL) ne créent les tables que
si elles n'existent pas : une base créée avant l'ajout d'une colonne ne la reçoit
pas. On ajoute ici les colonnes manquantes au démarrage, sans rien effacer.
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

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
    inspecteur = inspect(engine)
    tables = set(inspecteur.get_table_names())
    with engine.begin() as conn:
        for table, colonnes in COLONNES_AJOUTEES.items():
            if table not in tables:
                continue
            existantes = {c["name"] for c in inspecteur.get_columns(table)}
            for nom, definition in colonnes:
                if nom not in existantes:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {nom} {definition}"))
