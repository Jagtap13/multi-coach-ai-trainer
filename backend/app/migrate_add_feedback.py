import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "models"))

from database import engine
from user import User
from chat_history import ChatHistory
from feedback import MessageFeedback

print("Creating message_feedback table...")
MessageFeedback.__table__.create(bind=engine, checkfirst=True)
print("Migration complete.")