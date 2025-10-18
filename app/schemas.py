# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Identifiant unique de session utilisateur")
    message: str = Field(..., min_length=1, description="Message envoyé par l'utilisateur")

class ChatResponse(BaseModel):
    response: str  # Réponse générée par Konan
    id: Optional[int] = None
    history: Optional[List[str]] = None  # Contexte renvoyé (optionnel)
