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


# sans Docker


# La première fois
Terminal 1 : backend

python3 -m venv backend/venv
source backend/venv/bin/activate
python -m pip install -r backend/requirements.txt
export DATABASE_URL=sqlite:///./db.sqlite3
python -c "from backend.database import engine; from backend.models import Base; Base.metadata.create_all(engine)"
python -m uvicorn backend.main:app --reload

Terminal 2 : frontend

cd frontend/SonicBandFront
npm install
npm run dev
Ouvrir ensuite http://localhost:8080.

# Les fois suivantes
Terminal 1 : backend

source backend/venv/bin/activate
export DATABASE_URL=sqlite:///./db.sqlite3
python -m uvicorn backend.main:app --reload

Terminal 2 : frontend

cd frontend/SonicBandFront
npm run dev


chmod +x install.sh start.sh 
./install.sh
./start.sh  