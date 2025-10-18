import chromadb
from chromadb.config import Settings
import os

# Dossier de persistance
CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_store")
os.makedirs(CHROMA_DIR, exist_ok=True)

client = chromadb.Client(Settings(
    persist_directory=CHROMA_DIR,
    anonymized_telemetry=False
))

# Collection principale
collection = client.get_or_create_collection("lois_tunisiennes")

def add_document(title: str, content: str):
    """
    Ajoute un document juridique à la base vectorielle.
    """
    collection.add(
        documents=[content],
        metadatas=[{"title": title}],
        ids=[title]
    )

def search_law(query: str, n=3):
    """
    Recherche sémantique : renvoie les textes de loi pertinents.
    """
    try:
        results = collection.query(query_texts=[query], n_results=n)
        return [doc for doc in results["documents"][0]]
    except Exception as e:
        print("❌ Erreur recherche Chroma:", e)
        return []
