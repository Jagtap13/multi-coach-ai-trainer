from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, String
from sqlalchemy.sql import func
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from database import Base

class ProgressEntry(Base):
    __tablename__ = "progress_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    weight_kg = Column(Float, nullable=False)
    entry_date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())