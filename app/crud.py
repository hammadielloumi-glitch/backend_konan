from sqlalchemy.orm import Session
from app.models import Conversation

def create_conversation(db: Session, session_id: str, role: str, message_user: str = None, message_konan: str = None):
    conv = Conversation(
        session_id=session_id,
        role=role,
        message_user=message_user,
        message_konan=message_konan
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def get_conversations(db: Session, session_id: str):
    return db.query(Conversation).filter(Conversation.session_id == session_id).all()
