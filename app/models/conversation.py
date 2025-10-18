# app/models/conversation.py
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base  # Base doit venir de app/database.py


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)

    # 'user' ou 'assistant' (optionnel pour la suite)
    role = Column(String, default="user")

    # on stocke le message utilisateur et la réponse konan
    message_user = Column(Text, nullable=True)
    message_konan = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
