# ============================================
# app/main.py — Version corrigée Master Dev
# ============================================

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
from openai import OpenAI
from app.database import get_db, engine
from app.models import Conversation
from app.schemas import ChatRequest, ChatResponse
from app.memory_vector import store_memory, retrieve_similar_context
from app.memory_vector import router as memory_vector_router

import os
import traceback
import asyncio

# ======================================================
# 1️⃣ CONFIGURATION GLOBALE
# ======================================================
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, "..", ".env")
load_dotenv(env_path)

db_url = os.getenv("SQLALCHEMY_DATABASE_URL")
openai_key = os.getenv("OPENAI_API_KEY")

if not db_url:
    print("❌ ERREUR : SQLALCHEMY_DATABASE_URL non trouvé dans .env")
else:
    print(f"🔍 DATABASE_URL détectée : {db_url}")

if not openai_key:
    raise RuntimeError("❌ Clé OpenAI absente dans .env (OPENAI_API_KEY)")

client = OpenAI(api_key=openai_key)

# ======================================================
# 2️⃣ INSTANCE FASTAPI
# ======================================================
app = FastAPI(
    title="Konan API",
    version="1.4",
    description="Backend IA juridique tunisien - Projet Konan ⚖️"
)

# ======================================================
# 3️⃣ MIDDLEWARE CORS
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# 4️⃣ PROMPT SYSTÈME KONAN
# ======================================================
SYSTEM_PROMPT = """
Tu es **Konan ⚖️**, un assistant juridique master spécialisé en droit tunisien.
Mission : rendre la loi claire, fiable et accessible.
- Basé uniquement sur les textes légaux tunisiens.
- Cite les articles exacts ⚖️.
- Répond de façon claire et structurée.
- Fournis un exemple concret si possible.
- Pose une question complémentaire pour mieux cerner le cas.
- Analyse les documents si l’utilisateur en fournit.
- Si vulgarité → répondre par la loi.
- Si hors du droit tunisien → dire : "Je ne peux pas répondre car ce n’est pas une question juridique liée au droit tunisien."
"""

# ======================================================
# 5️⃣ ENDPOINT PRINCIPAL /api/chat
# ======================================================
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.message},
        ]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        konan_reply = completion.choices[0].message.content.strip()

        # 💾 Sauvegarde PostgreSQL
        db.add(Conversation(session_id=request.session_id, role="user", message_user=request.message))
        db.add(Conversation(session_id=request.session_id, role="assistant", message_konan=konan_reply))
        db.commit()

        # 🧠 Mémoire vectorielle
        store_memory(request.session_id, request.message, konan_reply)

        print(f"[✅ CHAT OK] session={request.session_id}")
        return ChatResponse(
            response=f"⚖️ Konan : {konan_reply}",
            id=None,
            history=None,
        )

    except Exception as e:
        db.rollback()
        print("[❌ ERREUR CHAT]", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur OpenAI : {str(e)}")

# ======================================================
# 6️⃣ CHECK SANTÉ
# ======================================================
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "KONAN API opérationnelle"}

# ======================================================
# 7️⃣ TEST POSTGRESQL
# ======================================================
@app.get("/test_db")
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()")).fetchone()
        return {"status": "DB OK", "timestamp": str(result[0])}
    except Exception as e:
        print("[❌ ERREUR DB]", e)
        return {"status": "DB ERROR", "error": str(e)}

# ======================================================
# 8️⃣ SHUTDOWN PROPRE
# ======================================================
@app.on_event("shutdown")
async def graceful_shutdown():
    print("🛑 Fermeture propre de KONAN API...")
    try:
        await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
    finally:
        print("✅ Fermeture terminée sans erreur asyncio.")

# ======================================================
# 9️⃣ ROUTEUR CHROMADB
# ======================================================
app.include_router(memory_vector_router)
