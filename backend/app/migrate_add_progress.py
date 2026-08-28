import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "models"))

from database import engine
from user import User
from progress import ProgressEntry

print("Creating progress_entries table...")
ProgressEntry.__table__.create(bind=engine, checkfirst=True)
print("Migration complete.")