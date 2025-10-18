from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .db import get_db, Base, engine
from .models import User, LawArticle
from .schemas import UserCreate, Token, ChatRequest, ChatResponse, PDFRequest, UserOut
from .core.security import hash_password, verify_password, create_access_token
from .services.search import semantic_search, upsert_documents
from .services.openai_client import chat_completion
from .services.pdf import make_simple_pdf
from .agents.registry import get_agent
import io

router = APIRouter()
Base.metadata.create_all(bind=engine)


# === Auth ===
@router.post("/auth/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=Token)
def login(data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# === Seed base lois + index Chroma ===
@router.post("/seed")
def seed_laws(db: Session = Depends(get_db)):
    articles = [
        {"domain": "famille", "reference": "الفصل 1", "text_ar": "ينظّم هذا القانون مسائل الزواج والطلاق والنفقة...", "text_fr": "Règle les questions du mariage, divorce, pension..."},
        {"domain": "travail", "reference": "الفصل 5", "text_ar": "يحدّد هذا الفصل حقوق العامل وساعات العمل...", "text_fr": "Définit les droits du travailleur et les horaires..."}
    ]
    for a in articles:
        if not db.query(LawArticle).filter(LawArticle.reference==a["reference"], LawArticle.domain==a["domain"]).first():
            db.add(LawArticle(**a))
    db.commit()

    # Préparation Chroma
    ids, docs, metas = [], [], []
    for a in db.query(LawArticle).all():
        text = a.text_ar or a.text_fr or ""
        ids.append(f"{a.domain}:{a.reference}")
        docs.append(text)
        metas.append({"domain": a.domain, "reference": a.reference})

    upsert_documents(docs, metas, ids)
    return {"status": "ok", "count": len(docs)}


# === Chat avec recherche + OpenAI ===
@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    hits = semantic_search(payload.message, n_results=5)

    agent = get_agent(payload.domain or "civil")
    messages = agent.build_prompt(payload.message, hits)

    if payload.history:
        messages.extend(payload.history)

    ai = await chat_completion(messages)
    answer = ai.get("content") if isinstance(ai, dict) else str(ai)

    citations = []
    if "metadatas" in hits:
        for meta in hits["metadatas"][0]:
            citations.append({
                "reference": meta.get("reference"),
                "domain": meta.get("domain")
            })

    return {"answer": answer, "citations": citations}


# === Export PDF ===
@router.post("/pdf")
def pdf(req: PDFRequest):
    content = req.content if req.content else "Konan Report"
    blob = make_simple_pdf(content)

    filename = req.filename if req.filename.endswith(".pdf") else f"{req.filename}.pdf"
    return StreamingResponse(io.BytesIO(blob), media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})
