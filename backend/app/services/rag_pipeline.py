import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "coaches"))

from retriever import retrieve_relevant_chunks
from ollama_client import generate_response
from coach_prompts import get_coach_prompt

def build_prompt(user_question, retrieved_chunks, coach_type, profile=None, conversation_history=None, avoided_exercises=None):
    context = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])
    coach_persona = get_coach_prompt(coach_type)

    profile_section =""
    if profile:
        details=[]
        if profile.get("age"):
            details.append(f"Age: {profile['age']}")
        if profile.get("weight_kg"):
            details.append(f"weight: {profile['weight_kg']} kg")
        if profile.get("experience_level"):
            details.append(f"Experience_level: {profile['experience_level']}")
        if profile.get("goal"):
            details.append(f"Goal: {profile['goal']}")
        if profile.get("gender"):
            details.append(f"Gender: {profile['gender']}")

        if details:
            profile_section = f"\nUser profile:\n{chr(10).join(details)}\n\nTailor your answer specifically to this user's profile above — consider their experience level and goal when giving advice.\n"

    history_section = ""
    if conversation_history:
        turns = []
        for turn in conversation_history:
            turns.append(f"User: {turn['question']}\nCoach: {turn['answer']}")
        history_section = f"\nPrevious conversation in this session:\n{chr(10).join(turns)}\n\nUse this prior context only if it's relevant to the current question below. Do not repeat it back verbatim.\n"

    avoid_section = ""
    if avoided_exercises and avoided_exercises.lower() != "none":
        avoid_section = f"\n\nHARD CONSTRAINT — DO NOT INCLUDE ANY OF THESE EXERCISES ANYWHERE IN YOUR ANSWER, under any day or section: {avoided_exercises}\nBefore finalizing your answer, check every single exercise name you plan to include against this list.\n"

    prompt = f"""{coach_persona}
    {profile_section}{history_section}

Use the following trusted fitness information to answer the user's question accurately. If the information doesn't fully answer the question, use your general knowledge but stay consistent with the provided context and your coaching persona.

Context:
{context}

Question: {user_question}{avoid_section}

Answer:"""
    return prompt

def extract_avoided_exercises(conversation_history):
    if not conversation_history:
        return None

    history_text = "\n".join(
        [f"User: {t['question']}\nCoach: {t['answer']}" for t in conversation_history]
    )
    extraction_prompt = f"""Read the following coaching conversation. List ONLY the specific exercise names that the coach said to avoid, are unsafe, or should not be done, due to injury or limitation. Respond with a short comma-separated list of exercise names only (e.g., "Overhead Press, Lateral Raises"). If no exercises were mentioned as something to avoid, respond with exactly: None

Conversation:
{history_text}

Exercises to avoid:"""

    result = generate_response(extraction_prompt)
    return result.strip()

EXERCISE_SYNONYMS = {
    "overhead press": ["overhead press", "military press", "shoulder press", "push press", "standing press"],
    "lateral raises": ["lateral raises", "lateral raise", "side raises", "side lateral raise"],
    "rear delt fly": ["rear delt fly", "rear delt flys", "rear delt flies", "reverse fly", "reverse flys"],
}

def expand_with_synonyms(exercise_name):
    key = exercise_name.strip().lower()
    for canonical, aliases in EXERCISE_SYNONYMS.items():
        if key == canonical or key in aliases:
            return aliases
    return [key]

def check_for_avoided_exercises(answer, avoided_exercises):
    if not avoided_exercises or avoided_exercises.lower() == "none":
        return answer

    exercise_list = [e.strip() for e in avoided_exercises.split(",") if e.strip()]
    found = []
    for exercise in exercise_list:
        aliases = expand_with_synonyms(exercise)
        if any(alias in answer.lower() for alias in aliases):
            found.append(exercise)

    if found:
        warning = f"\n\n⚠️ Note: This response mentions {', '.join(found)} (or a closely related variation), which you were advised earlier to avoid. Please double-check this against your injury or limitation before proceeding, or consult a professional."
        answer = answer + warning

    return answer

def get_rag_response(user_question, coach_type="bodybuilding", k=3, profile=None, conversation_history=None):
    chunks = retrieve_relevant_chunks(user_question, k=k, coach_type=coach_type)

    avoided_exercises = extract_avoided_exercises(conversation_history)

    prompt = build_prompt(user_question, chunks, coach_type=coach_type, profile=profile, conversation_history=conversation_history, avoided_exercises=avoided_exercises)
    answer = generate_response(prompt)
    answer = check_for_avoided_exercises(answer, avoided_exercises)
    return answer, chunks

# if __name__ == "__main__":
#     question = "What rep range should I use to build muscle?"

#     for coach in ["bodybuilding", "powerlifting", "nutrition", "fatloss"]:
#         print(f"\n{'='*50}")
#         print(f"Coach: {coach.upper()}")
#         print(f"Question: {question}\n")

#         answer, sources = get_rag_response(question, coach_type=coach)

#         print("--- Answer ---")
#         print(answer)

#         print("\n--- Sources used ---")
#         for chunk in sources:
#             import os
#             source = os.path.basename(chunk.metadata.get("source", "unknown"))
#             print(f"- {source}")

if __name__ == "__main__":
    question = "I have a shoulder injury but I really want to build muscle fast. What should I do?"
    sample_profile={
        "age":22,
        "weight_kg":65,
        "experience_level":"beginner",
        "goal":"build muscle"
    }
    answer, sources = get_rag_response(question,coach_type="bodybuilding",profile=sample_profile)
    print("--- Answer (with profile) ---")
    print(answer)