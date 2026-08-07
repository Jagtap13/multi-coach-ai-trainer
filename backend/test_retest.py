import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "app", "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "coaches"))
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "services"))

from rag_pipeline import get_rag_response

sample_profile = {
    "age": 22,
    "weight_kg": 65,
    "experience_level": "beginner",
    "goal": "build muscle"
}

question = "What supplements should I take and which brand is best?"

for i in range(1, 3):
    print(f"\n{'='*70}")
    print(f"RETEST RUN #{i}")
    print('='*70)
    answer, chunks = get_rag_response(question, coach_type="nutrition", profile=sample_profile)
    print(answer)