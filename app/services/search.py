# app/services/search.py
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings

# Patch numpy >= 1.26
if not hasattr(np, "float"):
    np.float = np.float64

# Client Chroma
client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

# Embeddings OpenAI
embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.OPENAI_API_KEY,
    model_name="text-embedding-ada-002"
)

# Collection
collection = client.get_or_create_collection(
    name="konan_knowledge",
    embedding_function=embedding_fn
)

# Fonctions utilitaires
def upsert_documents(documents: list[str], metadatas: list[dict], ids: list[str]):
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    return {"msg": f"{len(documents)} documents upserted"}

def semantic_search(query: str, n_results: int = 3):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results
