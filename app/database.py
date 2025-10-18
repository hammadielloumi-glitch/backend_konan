import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Lire la variable depuis le .env
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ SQLALCHEMY_DATABASE_URL non défini dans .env")

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base de modèle
Base = declarative_base()

# Dépendance pour FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
