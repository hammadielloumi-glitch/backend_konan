from sqlalchemy.orm import Session
from app.models.conversation import Conversation

# ✅ Ajouter un message dans la conversation
def add_message(db: Session, session_id: str, sender: str, message: str):
    """
    Ajoute un message à la table Conversation pour une session donnée.
    Si la session n'existe pas encore, elle est créée automatiquement.
    """
    new_message = Conversation(
        session_id=session_id,
        sender=sender,
        message=message
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


# ✅ Récupérer l'historique d'une session
def get_history(db: Session, session_id: str):
    """
    Retourne la liste de tous les messages enregistrés dans une session donnée.
    """
    messages = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.id.asc())
        .all()
    )
    return messages
