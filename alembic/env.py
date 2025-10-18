import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Charger les variables d'environnement depuis .env
load_dotenv()

# Lecture du DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:pass123@localhost:5432/konan_db")

# Configuration de base Alembic
config = context.config
fileConfig(config.config_file_name)

# Importer les modèles de l'application
from app.database import Base
from app.models import Conversation

target_metadata = Base.metadata

def run_migrations_online():
    """
    Exécute les migrations avec une connexion en ligne (active).
    """
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
