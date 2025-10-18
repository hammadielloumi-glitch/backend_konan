# app/memory.py
from sqlalchemy.orm import Session
from app import models

def add_message(db: Session, session_id: str, role: str, message: str):
    conv = models.Conversation(session_id=session_id, role=role, message=message)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def get_history(db: Session, session_id: str, limit: int = 5):
    return (
        db.query(models.Conversation)
        .filter(models.Conversation.session_id == session_id)
        .order_by(models.Conversation.created_at.desc())
        .limit(limit)
        .all()[::-1]  # renverser pour garder ordre chronologique
    )
