import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("Adding measurement columns to progress_entries...")
    conn.execute(text("ALTER TABLE progress_entries ADD COLUMN IF NOT EXISTS waist_cm FLOAT"))
    conn.execute(text("ALTER TABLE progress_entries ADD COLUMN IF NOT EXISTS chest_cm FLOAT"))
    conn.execute(text("ALTER TABLE progress_entries ADD COLUMN IF NOT EXISTS arms_cm FLOAT"))
    print("Adding goal_weight_kg to users...")
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS goal_weight_kg FLOAT"))
    conn.commit()
    print("Migration complete.")