import sys
import os
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

import youtube_service
from rag_pipeline import find_exercises
from rag_pipeline import find_exercises, merge_avoided_with_risk_map, INJURY_RISK_EXERCISES


class TestFindExercises:
    def test_finds_exercises_with_sets_and_reps(self):
        answer = "1. Leg Press: 3 sets of 8-12 reps\n2. Leg Extensions: 3 sets of 10-15 reps"
        assert find_exercises(answer) == ["leg press", "leg extension"]

    def test_skips_warmup_lines(self):
        answer = "Warm-up: jogging and lunges.\n1. Leg Press: 3 sets of 8-12 reps"
        assert find_exercises(answer) == ["leg press"]

    def test_longer_name_wins_romanian_deadlift(self):
        answer = "1. Romanian Deadlifts: 3 sets of 8 reps"
        assert find_exercises(answer) == ["romanian deadlift"]

    def test_longer_name_wins_bulgarian_split_squat(self):
        answer = "1. Bulgarian Split Squats: 3 sets of 8 reps"
        assert find_exercises(answer) == ["lunge"]

    def test_shoulder_injury_blocks_lat_pulldown(self):
        avoided = merge_avoided_with_risk_map(None, "shoulder", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Lat Pulldowns: 3 sets of 10 reps", avoided) == []

    def test_shoulder_injury_blocks_incline_bench_press(self):
        avoided = merge_avoided_with_risk_map(None, "shoulder", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Incline Bench Press: 3 sets of 8 reps", avoided) == []

    def test_elbow_injury_blocks_hammer_curl(self):
        avoided = merge_avoided_with_risk_map(None, "elbow", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Hammer Curls: 3 sets of 10 reps", avoided) == []

    def test_incline_bench_press_gets_its_own_video(self):
        assert find_exercises("1. Incline Bench Press: 3 sets of 8 reps") == ["incline bench press"]

    def test_lat_pulldown_gets_its_own_video(self):
        assert find_exercises("1. Lat Pulldowns: 3 sets of 10 reps") == ["lat pulldown"]

    def test_hammer_curl_gets_its_own_video(self):
        assert find_exercises("1. Hammer Curls: 3 sets of 10 reps") == ["hammer curl"]

    def test_elbow_injury_blocks_lat_pulldown(self):
        avoided = merge_avoided_with_risk_map(None, "elbow", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Lat Pulldowns: 3 sets of 10 reps", avoided) == []

    def test_wrist_injury_blocks_incline_bench_press(self):
        avoided = merge_avoided_with_risk_map(None, "wrist", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Incline Bench Press: 3 sets of 8 reps", avoided) == []

    def test_coach_said_avoid_bench_press_blocks_incline(self):
        assert find_exercises("1. Incline Bench Press: 3 sets of 8 reps", "Bench Press") == []

    def test_step_up_gets_its_own_video(self):
        assert find_exercises("1. Step-Ups: 3 sets of 10 reps") == ["step-up"]

    def test_knee_injury_blocks_step_up(self):
        avoided = merge_avoided_with_risk_map(None, "knee", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Step-Ups: 3 sets of 10 reps", avoided) == []

    def test_no_duplicate_entries(self):
        result = merge_avoided_with_risk_map("Squats", "knee", INJURY_RISK_EXERCISES)
        entries = [e.strip() for e in result.lower().split(",")]
        assert entries.count("squats") == 1

    def test_hip_injury_blocks_step_up(self):
        avoided = merge_avoided_with_risk_map(None, "hip", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Step-Ups: 3 sets of 10 reps", avoided) == []

    def test_wrist_injury_blocks_mountain_climber(self):
       avoided = merge_avoided_with_risk_map(None, "wrist", INJURY_RISK_EXERCISES)
       assert find_exercises("1. Mountain Climbers: 3 sets of 20 reps", avoided) == []


    def test_avoid_marker_skips_exercise(self):
        answer = "Avoid squats because of your knee.\n1. Leg Press: 3 sets of 8-12 reps"
        assert find_exercises(answer) == ["leg press"]

    def test_avoided_list_skips_exercise(self):
        answer = "1. Squats: 3 sets of 8 reps\n2. Lunges: 3 sets of 8 reps"
        assert find_exercises(answer, "Squat") == ["lunge"]

    def test_two_line_format(self):
        answer = "**Exercise 1: Leg Press**\n\n* 3 sets of 8-12 reps"
        assert find_exercises(answer) == ["leg press"]

    def test_goblet_squat_gets_its_own_video(self):
        assert find_exercises("1. Goblet Squats: 3 sets of 10 reps") == ["goblet squat"]

    def test_knee_injury_blocks_goblet_squat(self):
        avoided = merge_avoided_with_risk_map(None, "knee", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Goblet Squats: 3 sets of 10 reps", avoided) == []

    def test_chest_fly_gets_its_own_video(self):
        assert find_exercises("1. Dumbbell Flies: 3 sets of 12 reps") == ["chest fly"]

    def test_shoulder_injury_blocks_chest_fly(self):
        avoided = merge_avoided_with_risk_map(None, "shoulder", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Dumbbell Flies: 3 sets of 12 reps", avoided) == []

    def test_dip_gets_its_own_video(self):
        assert find_exercises("1. Tricep Dips: 3 sets of 10 reps") == ["dip"]

    def test_shoulder_injury_blocks_dip(self):
        avoided = merge_avoided_with_risk_map(None, "shoulder", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Tricep Dips: 3 sets of 10 reps", avoided) == []

    def test_elbow_injury_blocks_dip(self):
        avoided = merge_avoided_with_risk_map(None, "elbow", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Tricep Dips: 3 sets of 10 reps", avoided) == []

    def test_shoulder_injury_blocks_mountain_climber(self):
        avoided = merge_avoided_with_risk_map(None, "shoulder", INJURY_RISK_EXERCISES)
        assert find_exercises("1. Mountain Climbers: 3 sets of 20 reps", avoided) == []
    
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

        def test_cache_hit_does_not_call_youtube(self, monkeypatch):
            calls = []
            monkeypatch.setattr(youtube_service, "search_youtube",
                                lambda query, language="en": calls.append(query) or FAKE_VIDEOS)

            # a saved row that is fresh (fetched just now)
            row = MagicMock()
            row.fetched_at = datetime.now(timezone.utc)
            row.videos_json = json.dumps(FAKE_VIDEOS)

            db = MagicMock()
            db.query.return_value.filter.return_value.first.return_value = row   # lookup finds it

            result = youtube_service.get_videos_for_exercise("leg press", "en", db)

            assert result == FAKE_VIDEOS
            assert len(calls) == 0      # YouTube was never asked

    def test_youtube_failure_saves_nothing(self, monkeypatch):
        monkeypatch.setattr(youtube_service, "search_youtube",
                            lambda query, language="en": [])   # YouTube fails

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None   # nothing saved

        result = youtube_service.get_videos_for_exercise("leg press", "en", db)

        assert result == []
        db.add.assert_not_called()      # an empty result must not be saved

    def test_ambiguous_names_use_a_clearer_search_term(self, monkeypatch):
        queries = []
        monkeypatch.setattr(youtube_service, "search_youtube",
                            lambda query, language="en": queries.append(query) or FAKE_VIDEOS)

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        youtube_service.get_videos_for_exercise("clean", "en", db)

        assert "power clean" in queries[0]