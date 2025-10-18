# app/routers/memory_vector.py
import os
from fastapi import APIRouter
from chromadb import Client
from chromadb.config import Settings

router = APIRouter(prefix="/memory", tags=["Vector Memory"])

# Répertoire persistant
CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_store")
os.makedirs(CHROMA_DIR, exist_ok=True)

# Initialisation du client Chroma
chroma_client = Client(
    Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    )
)

@router.get("/stats")
def get_chroma_stats():
    """Retourne les statistiques de la mémoire vectorielle ChromaDB."""
    try:
        collections = chroma_client.list_collections()
        total = len(collections)
        names = [c.name for c in collections]

        return {
            "status": "ok",
            "total_collections": total,
            "collections": names,
            "message": "📊 Statistiques mémoire vectorielle OK"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur d'accès à ChromaDB : {str(e)}"
        }
