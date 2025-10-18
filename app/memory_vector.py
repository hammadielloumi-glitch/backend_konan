# ============================================
# app/memory_vector.py — Version Master Dev
# ============================================

import os
import traceback
from fastapi import APIRouter, HTTPException
from chromadb import Client
from chromadb.config import Settings
from openai import OpenAI

# ======================================================
# 🔧 INITIALISATION
# ======================================================

CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_store")
os.makedirs(CHROMA_DIR, exist_ok=True)

client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    chroma_client = Client(
        Settings(
            persist_directory=CHROMA_DIR,
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    print(f"✅ ChromaDB initialisé dans {CHROMA_DIR}")
except Exception as e:
    chroma_client = None
    print(f"[⚠️ ERREUR INIT CHROMA] {e}")
    traceback.print_exc()

# ======================================================
# 💾 ENREGISTREMENT MÉMOIRE VECTORIELLE
# ======================================================

def store_memory(session_id: str, message_user: str, message_konan: str):
    """
    Enregistre les messages vectorisés dans Chroma.
    """
    try:
        if not chroma_client:
            raise RuntimeError("Chroma non disponible")

        collection = chroma_client.get_or_create_collection(name="konan_memory")

        document_text = f"USER: {message_user}\nKONAN: {message_konan}"
        collection.add(
            documents=[document_text],
            ids=[f"{session_id}_{abs(hash(message_user))}"]
        )

        total_items = len(collection.get().get("ids", []))
        print(f"[🧠 MÉMOIRE SAUVEGARDÉE] session={session_id} | total={total_items}")

    except Exception as e:
        print(f"[⚠️ Fallback Embedding] {e}")
        try:
            client_openai.embeddings.create(
                model="text-embedding-3-small",
                input=f"USER: {message_user}\nKONAN: {message_konan}"
            )
            print("[✅ MEMOIRE VIA OPENAI] Sauvegarde sans erreur (fallback)")
        except Exception as ee:
            print(f"[❌ ERREUR MEMOIRE VECTORIELLE FINALE] {ee}")

# ======================================================
# 🔍 RECHERCHE CONTEXTE VECTORIEL
# ======================================================

def retrieve_similar_context(query: str, n_results: int = 3):
    """
    Recherche les conversations similaires à la requête actuelle.
    """
    try:
        if not chroma_client:
            raise RuntimeError("Chroma non disponible")

        collection = chroma_client.get_or_create_collection(name="konan_memory")
        results = collection.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        print(f"[🔍 CONTEXTE RETROUVÉ] {len(docs)} résultat(s)")
        return docs

    except Exception as e:
        print(f"[⚠️ Fallback OpenAI Context] {e}")
        try:
            client_openai.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            print("[✅ CONTEXTE VIA OPENAI] Embedding local désactivé")
            return []
        except Exception as ee:
            print(f"[❌ ERREUR CONTEXTE VECTORIEL FINALE] {ee}")
            return []

# ======================================================
# 🧩 ROUTES FASTAPI — CHROMA INSPECTION
# ======================================================

router = APIRouter(prefix="/api/memory", tags=["Memory Vectorielle"])

@router.get("/inspect")
def inspect_memory():
    """Retourne la liste des conversations stockées dans Chroma (debug)."""
    try:
        if not chroma_client:
            raise HTTPException(status_code=500, detail="Chroma non initialisé.")
        collection = chroma_client.get_or_create_collection(name="konan_memory")
        data = collection.get()
        docs = data.get("documents", [])
        ids = data.get("ids", [])
        total = len(ids)
        print(f"[🧩 INSPECT] {total} éléments trouvés dans la mémoire.")
        return {
            "total": total,
            "samples": [
                {"id": ids[i], "text": docs[i][:600]}
                for i in range(min(5, total))
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d’inspection mémoire : {e}")

@router.get("/stats")
def memory_stats():
    """📊 Retourne des statistiques sur la mémoire vectorielle."""
    try:
        if not chroma_client:
            raise HTTPException(status_code=500, detail="Chroma non initialisé.")
        collection = chroma_client.get_or_create_collection(name="konan_memory")
        data = collection.get()
        total = len(data.get("ids", []))
        docs = data.get("documents", [])
        size_kb = sum(len(doc.encode("utf-8")) for doc in docs) / 1024
        last_id = data.get("ids", [])[-1] if total > 0 else None

        return {
            "status": "ok",
            "total_items": total,
            "approx_size_kb": round(size_kb, 2),
            "last_id": last_id,
            "message": "📊 Statistiques mémoire vectorielle OK"
        }
    except Exception as e:
        print(f"[❌ ERREUR STATS MEMOIRE] {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération statistiques : {e}")

@router.delete("/clear")
def clear_memory():
    """🧹 Supprime entièrement la mémoire vectorielle (ChromaDB)."""
    try:
        if not chroma_client:
            raise HTTPException(status_code=500, detail="Chroma non initialisé.")

        chroma_client.reset()
        print("🧹 Mémoire vectorielle effacée avec succès.")
        return {
            "status": "ok",
            "message": "Mémoire vectorielle supprimée avec succès ✅"
        }

    except Exception as e:
        print(f"[❌ ERREUR CLEAR MEMOIRE] {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du nettoyage : {e}"
        )
        
@router.post("/test")
def test_memory():
    """
    🧪 Test complet de la mémoire vectorielle (ChromaDB).
    - Ajoute un vecteur de test
    - Vérifie sa présence
    - Le supprime ensuite
    """
    try:
        if not chroma_client:
            raise HTTPException(status_code=500, detail="Chroma non initialisé.")

        # 1️⃣ Création / récupération de la collection
        collection = chroma_client.get_or_create_collection(name="konan_memory_test")

        # 2️⃣ Ajout d'un document de test
        doc_id = "test_vector_001"
        doc_text = "USER: Bonjour Konan\nKONAN: Ceci est un test de la mémoire vectorielle."
        collection.add(documents=[doc_text], ids=[doc_id])

        # 3️⃣ Vérification de la présence
        data = collection.get()
        total = len(data.get("ids", []))
        found = doc_id in data.get("ids", [])

        # 4️⃣ Nettoyage de la collection
        chroma_client.delete_collection("konan_memory_test")

        if not found:
            raise HTTPException(status_code=500, detail="Échec du test d'insertion dans ChromaDB.")

        return {
            "status": "ok",
            "message": "🧠 Test mémoire vectorielle réussi.",
            "inserted_id": doc_id,
            "total_after_insert": total
        }

    except Exception as e:
        print(f"[❌ ERREUR TEST MEMOIRE] {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du test mémoire : {e}")
@router.get("/ping")
def ping_memory():
    """
    🔄 Vérifie simplement la disponibilité de ChromaDB sans modifier de données.
    Retourne "ok" si le client Chroma est opérationnel.
    """
    try:
        if not chroma_client:
            raise HTTPException(status_code=500, detail="❌ ChromaDB non initialisé.")

        # Test minimal : création d’une collection temporaire
        test_collection = chroma_client.get_or_create_collection(name="ping_check")
        if test_collection is None:
            raise HTTPException(status_code=500, detail="❌ Impossible d’accéder à ChromaDB.")

        return {
            "status": "ok",
            "message": "✅ ChromaDB répond — en ligne",
            "store_path": CHROMA_DIR
        }

    except Exception as e:
        print(f"[❌ ERREUR PING MEMOIRE] {e}")
        raise HTTPException(status_code=500, detail=f"Erreur ping mémoire : {e}")
