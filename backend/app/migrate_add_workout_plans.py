import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "models"))

from database import engine
from user import User
from workout_plan import WorkoutPlan

print("Creating workout_plans table...")
WorkoutPlan.__table__.create(bind=engine, checkfirst=True)
print("Migration complete.")