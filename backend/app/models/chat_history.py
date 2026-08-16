from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    coach_type = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(String, nullable=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())