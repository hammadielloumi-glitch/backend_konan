from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")  # Test connexion PostgreSQL
        return {"status": "ok", "database": "connected", "message": "API opérationnelle ✅"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "message": str(e)}
