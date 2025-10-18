import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# === Ajustement du chemin pour import ===
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# === Charger les variables d'environnement ===
load_dotenv()

# === Lecture de l’URL depuis Render ou .env ===
# Render injecte automatiquement DATABASE_URL dans l’environnement
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("SQLALCHEMY_DATABASE_URL")
    or "postgresql+psycopg2://postgres:pass123@localhost:5432/konan_db"
)

# === Config de base Alembic ===
config = context.config
fileConfig(config.config_file_name)

# === Import des modèles SQLAlchemy ===
from app.database import Base
from app.models import Conversation

target_metadata = Base.metadata

def run_migrations_online():
    """Exécute les migrations Alembic en ligne."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
