import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "app", "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "models"))

from database import SessionLocal
from chat_history import ChatHistory

db = SessionLocal()
records = db.query(ChatHistory).all()

print(f"Total records: {len(records)}\n")
for r in records:
    print(f"[{r.id}] conversation_id={r.conversation_id} | coach={r.coach_type} | Q: {r.question[:40]}...")

db.close()