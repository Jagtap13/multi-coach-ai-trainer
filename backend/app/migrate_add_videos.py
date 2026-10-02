import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

from sqlalchemy import text
from database import engine

print("Adding videos column to chat_history...")
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS videos TEXT"))
print("Migration complete.")