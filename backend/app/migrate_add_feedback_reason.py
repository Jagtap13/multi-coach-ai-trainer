import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("Adding reason column to message_feedback table...")
    conn.execute(text("ALTER TABLE message_feedback ADD COLUMN IF NOT EXISTS reason VARCHAR"))
    conn.commit()
    print("Migration complete.")