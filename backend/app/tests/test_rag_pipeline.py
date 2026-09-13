import sys
import os
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "coaches"))

from rag_pipeline import (
    expand_with_synonyms,
    check_for_avoided_items,
    merge_avoided_with_risk_map,
    extract_plan_structure,
    INJURY_RISK_EXERCISES,
    ALLERGY_RISK_FOODS,
)


class TestSynonymExpansion:
    def test_exact_match_returns_all_aliases(self):
        aliases = expand_with_synonyms("Overhead Press", "bodybuilding")
        assert "military press" in aliases
        assert "shoulder press" in aliases

    def test_alias_match_returns_full_group(self):
        aliases = expand_with_synonyms("Military Press", "bodybuilding")
        assert "overhead press" in aliases

    def test_unknown_exercise_falls_back_to_itself(self):
        aliases = expand_with_synonyms("Face Pulls", "bodybuilding")
        assert aliases == ["face pulls"]

    def test_nutrition_uses_food_synonyms_not_exercise(self):
        aliases = expand_with_synonyms("Dairy", "nutrition")
        assert "milk" in aliases
        assert "overhead press" not in aliases


class TestAvoidedItemsCheck:
    def test_flags_genuine_violation(self):
        answer = "Try Standing Military Press for 3 sets."
        result = check_for_avoided_items(answer, "Overhead Press", "bodybuilding")
        assert "⚠️" in result

    def test_no_warning_when_nothing_avoided(self):
        answer = "Try Bench Press for 3 sets."
        result = check_for_avoided_items(answer, "None", "bodybuilding")
        assert "⚠️" not in result

    def test_no_false_positive_on_safe_milk_alternative(self):
        answer = "Try almond milk or coconut milk instead of dairy."
        result = check_for_avoided_items(answer, "Dairy", "nutrition")
        assert "⚠️" not in result

    def test_no_false_positive_when_restating_condition(self):
        answer = "Given your lactose intolerance and peanut allergy, here is a safe plan using eggs and chicken."
        result = check_for_avoided_items(answer, "Peanuts, Lactose", "nutrition")
        assert "⚠️" not in result

    def test_flags_real_allergen_outside_safe_context(self):
        answer = "Add a scoop of whey protein to your shake."
        merged_items = merge_avoided_with_risk_map("Dairy", "dairy", ALLERGY_RISK_FOODS)
        result = check_for_avoided_items(answer, merged_items, "nutrition")
        assert "⚠️" in result


class TestInjuryAllergyRiskMerging:
    def test_merges_injury_risk_into_avoided_list(self):
        result = merge_avoided_with_risk_map("Running", "knee", INJURY_RISK_EXERCISES)
        assert "Running" in result
        assert "Squats" in result or "squats" in result.lower()

    def test_no_duplicate_entries(self):
        result = merge_avoided_with_risk_map("Squats", "knee", INJURY_RISK_EXERCISES)
        assert result.lower().count("squats") == 1

    def test_allergy_risk_map_used_for_nutrition(self):
        result = merge_avoided_with_risk_map("Dairy", "dairy", ALLERGY_RISK_FOODS)
        assert "Whey Protein" in result or "whey protein" in result.lower()

    def test_none_avoided_items_still_adds_risk_list(self):
        result = merge_avoided_with_risk_map(None, "shoulder", INJURY_RISK_EXERCISES)
        assert result is not None
        assert len(result) > 0


class TestPlanStructureExtraction:
    @patch("rag_pipeline.generate_response")
    def test_parses_valid_json(self, mock_generate):
        mock_generate.return_value = '{"days": [{"label": "Day 1", "items": ["Bench Press"]}]}'
        result = extract_plan_structure("some answer text", "bodybuilding")
        assert result is not None
        assert result["days"][0]["label"] == "Day 1"

    @patch("rag_pipeline.generate_response")
    def test_handles_markdown_wrapped_json(self, mock_generate):
        mock_generate.return_value = '```json\n{"days": [{"label": "Day 1", "items": ["Squats"]}]}\n```'
        result = extract_plan_structure("some answer text", "bodybuilding")
        assert result is not None
        assert result["days"][0]["items"] == ["Squats"]

    @patch("rag_pipeline.generate_response")
    def test_returns_none_for_no_plan(self, mock_generate):
        mock_generate.return_value = "NONE"
        result = extract_plan_structure("just a general answer", "bodybuilding")
        assert result is None

    @patch("rag_pipeline.generate_response")
    def test_returns_none_for_malformed_json(self, mock_generate):
        mock_generate.return_value = "this is not json at all"
        result = extract_plan_structure("some answer text", "bodybuilding")
        assert result is None