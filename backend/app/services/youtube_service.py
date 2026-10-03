import os
import html
import requests
import sys
import json

from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))

from exercise_video import ExerciseVideo

load_dotenv()

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def search_youtube(query, language="en"):
    """Return a list of up to 3 videos: [{video_id, title, channel, thumbnail}]"""
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        return []

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 3,
        "videoEmbeddable": "true",
        "safeSearch": "strict",
        "relevanceLanguage": language,
        "key": key,
    }

    try:
        response = requests.get(SEARCH_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"[youtube] search failed: {e}")
        return []

    videos = []
    for item in data.get("items", []):
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": html.unescape(item["snippet"]["title"]),
            "channel": item["snippet"]["channelTitle"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
        })
    return videos

CACHE_DAYS = 30


def get_videos_for_exercise(exercise, language, db):
    exercise = exercise.strip().lower()

    row = db.query(ExerciseVideo).filter(
        ExerciseVideo.exercise == exercise,
        ExerciseVideo.language == language,
    ).first()

    # 1. Is there a saved answer that is still fresh?
    if row and datetime.now(timezone.utc) - row.fetched_at < timedelta(days=CACHE_DAYS):
        print(f"[youtube] cache hit: {exercise}")
        return json.loads(row.videos_json)

    SEARCH_TERMS = {
        "clean": "power clean",
        "dip": "tricep dip",
        "good morning": "good morning barbell exercise",
        }
    # 2. No (or too old): ask YouTube
    print(f"[youtube] searching YouTube for: {exercise}")
    term = SEARCH_TERMS.get(exercise, exercise)
    videos = search_youtube(f"{term} proper form tutorial", language)

    # 3. If YouTube gave nothing (error, quota), do NOT save anything
    if not videos:
        return []

    # 4. Save the answer for next time
    if row:
        row.videos_json = json.dumps(videos)
        row.fetched_at = datetime.now(timezone.utc)
    else:
        db.add(ExerciseVideo(
            exercise=exercise,
            language=language,
            videos_json=json.dumps(videos),
        ))
    db.commit()
    return videos


if __name__ == "__main__":
    from database import SessionLocal
    db = SessionLocal()
    try:
        for v in get_videos_for_exercise("squat", "en", db):
            print(v)
    finally:
        db.close()