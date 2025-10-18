import os
from chromadb import Client
from chromadb.config import Settings

# Répertoire de stockage persistant
CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_store")
os.makedirs(CHROMA_DIR, exist_ok=True)

# Création du client Chroma
chroma_client = Client(
    Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    )
)
