import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("Adding conversation_id column...")
    conn.execute(text("ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS conversation_id VARCHAR"))
    conn.commit()

    print("Backfilling existing rows with legacy conversation IDs (grouped by user + coach)...")
    conn.execute(text("""
        UPDATE chat_history
        SET conversation_id = 'legacy-' || user_id || '-' || coach_type
        WHERE conversation_id IS NULL
    """))
    conn.commit()

    print("Migration complete.")
    