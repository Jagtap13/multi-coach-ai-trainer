import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "app", "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "coaches"))
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "services"))

from rag_pipeline import get_rag_response

def run_test(label, question, coach_type, profile=None):
    print(f"\n{'='*70}")
    print(f"TEST: {label}")
    print('='*70)
    try:
        answer, chunks = get_rag_response(question, coach_type=coach_type, profile=profile)
        print(answer)
    except Exception as e:
        print(f"ERROR: {e}")

sample_profile = {"age": 22, "weight_kg": 65, "experience_level": "beginner", "goal": "build muscle"}

# Retest the off-topic bug specifically
run_test("Off-Topic Redirect Check", "Can you help me write a Python script to scrape a website?", "bodybuilding", sample_profile)

# Retest consistency with lower temperature
run_test("Consistency Retest #1", "Give me a full daily diet plan for building muscle", "nutrition", sample_profile)
run_test("Consistency Retest #2", "Give me a full daily diet plan for building muscle", "nutrition", sample_profile)

print(f"\n{'='*70}")
print("COMBINED FIXES TEST COMPLETE")
print('='*70)