from fastapi import APIRouter
from app.services.search import semantic_search, upsert_documents

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/upsert")
def add_docs():
    docs = ["Article 1 de la Constitution...", "Article 2 du Code du Travail..."]
    metas = [{"source": "constitution"}, {"source": "travail"}]
    ids = ["doc1", "doc2"]

    return upsert_documents(docs, metas, ids)


@router.get("/")
def search_docs(q: str):
    return semantic_search(q, n_results=3)
