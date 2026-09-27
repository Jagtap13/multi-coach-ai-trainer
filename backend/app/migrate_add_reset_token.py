"""
Migration: add password reset token columns to users table.
Run manually: python migrate_add_reset_token.py
Kept as historical record, not deleted after running.
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR"
    ))
    conn.execute(text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP WITH TIME ZONE"
    ))
    conn.commit()

print("Migration complete: reset_token and reset_token_expires columns added to users table.")