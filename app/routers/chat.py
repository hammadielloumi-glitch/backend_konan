from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Conversation
from app.schemas import ChatRequest, ChatResponse
from app.memory_vector import store_memory, retrieve_similar_context
from app.utils.lang_detector import detect_language
from app.vector.chroma_manager import search_law
from openai import OpenAI
import os, traceback

# ======================================================
# 🔧 INITIALISATION
# ======================================================
router = APIRouter(prefix="/api", tags=["chat"])
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Tu es Konan ⚖️, assistant juridique tunisien.
Tu comprends l’arabe, le français et le dialecte tunisien.
Tu dois toujours répondre, même si la question est dialectale.
Baser toute réponse sur le droit tunisien, citer les articles pertinents et donner un exemple concret.
Si la question est vulgaire, réponds calmement en rappelant la loi.
"""

# ======================================================
# 🧠 HISTORIQUE
# ======================================================
def get_conversation_history(db: Session, session_id: str, limit: int = 10):
    try:
        records = (
            db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.created_at.asc())
            .limit(limit)
            .all()
        )
        history = []
        for rec in records:
            if rec.message_user:
                history.append({"role": "user", "content": rec.message_user})
            if rec.message_konan:
                history.append({"role": "assistant", "content": rec.message_konan})
        return history
    except Exception as e:
        print("[❌ ERREUR HISTORIQUE]", e)
        return []

# ======================================================
# 💬 ENDPOINT CHAT PRINCIPAL
# ======================================================
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        print(f"[📨 MESSAGE REÇU] session={request.session_id} | texte={request.message}")

        # 1️⃣ Détection automatique de la langue
        detected_lang = detect_language(request.message)
        if detected_lang == "ar":
            lang_prompt = "Réponds en arabe tunisien clair, fondé sur le droit tunisien."
        elif detected_lang == "fr":
            lang_prompt = "Réponds en français clair et professionnel."
        else:
            lang_prompt = "Réponds en dialecte tunisien simple, selon le droit tunisien."

        # 2️⃣ Historique conversationnel
        history = get_conversation_history(db, request.session_id)

        # 3️⃣ Recherche contextuelle (mémoire vectorielle)
        context_laws = search_law(request.message)
        context_text = "\n\n".join(context_laws) if context_laws else ""

        # 4️⃣ Construction du prompt complet
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": f"Contexte lois pertinentes :\n{context_text}"},
            {"role": "assistant", "content": lang_prompt},
        ] + history + [
            {"role": "user", "content": request.message},
        ]

        # 5️⃣ Requête OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
            max_tokens=800,
        )
        konan_reply = completion.choices[0].message.content.strip()

        # 6️⃣ Sauvegarde (PostgreSQL + vecteurs)
        db.add(Conversation(session_id=request.session_id, role="user", message_user=request.message))
        db.add(Conversation(session_id=request.session_id, role="assistant", message_konan=konan_reply))
        db.commit()
        store_memory(request.session_id, request.message, konan_reply)

        print(f"[✅ CHAT OK] Langue={detected_lang}")

        # 7️⃣ Réponse frontend
        return ChatResponse(
            response=f"⚖️ Konan : {konan_reply}",
            id=None,
            history=[m["content"] for m in messages[-10:]],
        )

    except Exception as e:
        db.rollback()
        print("[❌ ERREUR CHAT]", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# ======================================================
# 🩺 ROUTE SANTÉ
# ======================================================
@router.get("/health")
def health():
    return {"status": "ok", "message": "KONAN API IA multilingue + ChromaDB ✅"}
