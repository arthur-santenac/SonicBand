"""Configuration du backend, lue depuis les variables d'environnement (ou un fichier .env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Connexion PostgreSQL (mêmes valeurs par défaut que docker-compose.yml).
    database_url: str = "postgresql+psycopg://sonicband:sonicband@localhost:5432/sonicband"

    # Clé de signature des JWT : à remplacer absolument hors développement local.
    jwt_secret: str = "dev-secret-a-changer-absolument-en-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    # Origines autorisées pour le frontend (séparées par des virgules).
    cors_origins: str = "http://localhost:8080,http://127.0.0.1:8080"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
