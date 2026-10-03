import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "models"))
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))

from database import SessionLocal
from rag_pipeline import EXERCISE_SYNONYMS
from youtube_service import get_videos_for_exercise

db = SessionLocal()
try:
    for name in EXERCISE_SYNONYMS:
        videos = get_videos_for_exercise(name, "en", db)
        if videos:
            v = videos[0]
            print(f"{name:22} | {v['title'][:45]} | {v['channel']} | https://www.youtube.com/watch?v={v['video_id']}")
        else:
            print(f"{name:22} | NO VIDEOS")
        time.sleep(0.5)
finally:
    db.close()
    