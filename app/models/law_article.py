from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class LawArticle(Base):
    __tablename__ = "law_articles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
