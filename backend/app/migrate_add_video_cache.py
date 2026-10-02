import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "models"))

from database import engine
from exercise_video import ExerciseVideo

print("Creating exercise_videos table...")
ExerciseVideo.__table__.create(bind=engine, checkfirst=True)
print("Migration complete.")