"""Point d'entrée de l'API SonicBand.

Lancer en local depuis la racine du dépôt :
    uvicorn backend.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import router as auth_router
from backend.config import get_settings
from backend.equipements import router as equipements_router
from backend.groupes import router as groupes_router
from backend.repertoires import router as repertoires_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Sans Docker (SQLite), on crée au démarrage les tables qui manquent
    # (ex. « invitation » sur une base créée avant). Rien n'est effacé.
    # Avec Docker (PostgreSQL), c'est database/init.sql qui crée les tables.
    from backend.database import engine

    if get_settings().database_url.startswith("sqlite"):
        from backend.models import Base

        Base.metadata.create_all(engine)
    yield


app = FastAPI(title="SonicBand API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(groupes_router)
app.include_router(equipements_router)
app.include_router(repertoires_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
