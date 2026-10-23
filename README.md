# SonicBand
Outil libre de gestion de groupes de musique.

# Instructions d'utilisation

Une fois que vous avez récuperer le projet github.

Taper ces commandes dans votre terminal :

- docker compose up -d

optionel pour vérifier l'état après première commande : docker compose ps

- cd frontend/SonicBandFront/

- npm install

- npm run dev

## Modèles de la base de données

Les modèles SQLAlchemy 2 du backend se trouvent dans `backend/models.py` et correspondent aux tables définies dans `database/init.sql`.

Pour installer les dépendances Python :


- pip install -r backend/requirements.txt


Les modèles peuvent ensuite être importés ainsi :

La base PostgreSQL est initialisée par Docker Compose ; les modèles ne créent pas automatiquement les tables.
