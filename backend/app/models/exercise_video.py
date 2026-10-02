from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from database import Base


class ExerciseVideo(Base):
    __tablename__ = "exercise_videos"

    id = Column(Integer, primary_key=True, index=True)
    exercise = Column(String, nullable=False, index=True)   # e.g. "squat"
    language = Column(String, nullable=False)               # e.g. "en"
    videos_json = Column(Text, nullable=False)              # list of videos, saved as text
    fetched_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),   # set when the row is first created
        onupdate=func.now(),         # updated whenever the row is refreshed
    )

    __table_args__ = (
        UniqueConstraint("exercise", "language", name="uq_exercise_language"),
    )