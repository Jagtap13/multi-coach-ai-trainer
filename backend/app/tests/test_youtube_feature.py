import sys
import os
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

import youtube_service
from rag_pipeline import find_exercises


class TestFindExercises:
    def test_finds_exercises_with_sets_and_reps(self):
        answer = "1. Leg Press: 3 sets of 8-12 reps\n2. Leg Extensions: 3 sets of 10-15 reps"
        assert find_exercises(answer) == ["leg press", "leg extension"]

    def test_skips_warmup_lines(self):
        answer = "Warm-up: jogging and lunges.\n1. Leg Press: 3 sets of 8-12 reps"
        assert find_exercises(answer) == ["leg press"]

    def test_accepts_3x10_format(self):
        answer = "Squats 3x10\nLeg Press 4 x 8"
        assert find_exercises(answer) == ["squat", "leg press"]

    def test_returns_up_to_four_exercises(self):
        answer = (
            "1. Squats: 3 sets of 8 reps\n"
            "2. Leg Press: 3 sets of 8 reps\n"
            "3. Leg Curls: 3 sets of 8 reps\n"
            "4. Calf Raises: 3 sets of 8 reps\n"
            "5. Bench Press: 3 sets of 8 reps"
        )
        assert find_exercises(answer) == ["squat", "leg press", "leg curl", "calf raise"]


FAKE_VIDEOS = [{"video_id": "abc123", "title": "Leg Press Form",
                "channel": "Test Channel", "thumbnail": "http://example.com/t.jpg"}]


class TestVideoCache:
    def test_cache_miss_searches_youtube_and_saves(self, monkeypatch):
        calls = []
        monkeypatch.setattr(youtube_service, "search_youtube",
                            lambda query, language="en": calls.append(query) or FAKE_VIDEOS)

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None  # nothing saved yet

        result = youtube_service.get_videos_for_exercise("leg press", "en", db)

        assert result == FAKE_VIDEOS
        assert len(calls) == 1          # YouTube was asked once
        db.add.assert_called_once()     # and the answer was saved