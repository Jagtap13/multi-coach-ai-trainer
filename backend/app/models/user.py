from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Profile fields (kept simple - one table for now)
    age = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    experience_level = Column(String, nullable=True)
    goal = Column(String, nullable=True)