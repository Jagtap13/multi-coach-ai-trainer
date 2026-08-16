import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("Adding gender column to users table...")
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR"))
    conn.commit()
    print("Migration complete.")