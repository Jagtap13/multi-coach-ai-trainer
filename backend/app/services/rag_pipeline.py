import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "coaches"))

from retriever import retrieve_relevant_chunks
from ollama_client import generate_response
from coach_prompts import get_coach_prompt

COACH_ITEM_TYPE = {
    "bodybuilding": "exercise",
    "powerlifting": "exercise",
    "fatloss": "exercise",
    "nutrition": "food or ingredient",
}

EXERCISE_SYNONYMS = {
    "overhead press": ["overhead press", "military press", "shoulder press", "push press", "standing press"],
    "lateral raises": ["lateral raises", "lateral raise", "side raises", "side lateral raise"],
    "rear delt fly": ["rear delt fly", "rear delt flys", "rear delt flies", "reverse fly", "reverse flys"],
    "squat": ["squat", "squats", "back squat", "front squat", "box squat"],
    "deadlift": ["deadlift", "deadlifts", "conventional deadlift", "sumo deadlift"],
    "running": ["running", "jogging", "sprinting", "treadmill running"],
    "lunge": ["lunge", "lunges", "walking lunge", "bulgarian split squat"],
    "good morning": ["good morning", "good mornings"],
    "bent-over row": ["bent-over row", "bent-over rows", "barbell row", "barbell rows"],
}

FOOD_SYNONYMS = {
    "dairy": ["dairy", "milk", "cheese", "yogurt", "cream"],
    "peanuts": ["peanuts", "peanut butter", "peanut"],
    "gluten": ["gluten", "wheat", "bread", "pasta", "flour"],
    "shellfish": ["shellfish", "shrimp", "prawns", "crab", "lobster"],
    "eggs": ["eggs", "egg", "egg whites"],
    "soy": ["soy", "soybean", "tofu", "soy sauce"],
}

INJURY_RISK_EXERCISES = {
    "knee": ["squat", "squats", "lunge", "lunges", "box jump", "box jumps", "jumping", "running"],
    "shoulder": ["overhead press", "lateral raise", "lateral raises", "rear delt fly", "push press"],
    "lower back": ["deadlift", "deadlifts", "good morning", "good mornings", "bent-over row", "bent-over rows"],
    "hip": ["squat", "squats", "lunge", "lunges", "deadlift", "deadlifts"],
    "wrist": ["push-up", "push-ups", "bench press", "front squat"],
    "ankle": ["running", "jumping", "box jump", "box jumps", "lunge", "lunges"],
}

def get_synonym_map(coach_type):
    return FOOD_SYNONYMS if coach_type == "nutrition" else EXERCISE_SYNONYMS

def build_prompt(user_question, retrieved_chunks, coach_type, profile=None, conversation_history=None, avoided_items=None):
    context = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])
    coach_persona = get_coach_prompt(coach_type)
    item_type = COACH_ITEM_TYPE.get(coach_type, "exercise")

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
    if avoided_items and avoided_items.lower() != "none":
        avoid_section = f"\n\nHARD CONSTRAINT — DO NOT INCLUDE ANY OF THESE {item_type.upper()}S ANYWHERE IN YOUR ANSWER: {avoided_items}\nBefore finalizing your answer, check everything you plan to include against this list.\n"

    prompt = f"""{coach_persona}
    {profile_section}{history_section}

Use the following trusted fitness information to answer the user's question accurately. If the information doesn't fully answer the question, use your general knowledge but stay consistent with the provided context and your coaching persona.

Context:
{context}

Question: {user_question}{avoid_section}

Answer:"""
    return prompt

def expand_with_synonyms(item_name, coach_type):
    synonyms = get_synonym_map(coach_type)
    key = item_name.strip().lower()
    for canonical, aliases in synonyms.items():
        if key == canonical or key in aliases:
            return aliases
    return [key]

def check_for_avoided_items(answer, avoided_items, coach_type):
    if not avoided_items or avoided_items.lower() == "none":
        return answer

    item_list = [e.strip() for e in avoided_items.split(",") if e.strip()]
    found = []
    for item in item_list:
        aliases = expand_with_synonyms(item, coach_type)
        if any(alias in answer.lower() for alias in aliases):
            found.append(item)

    if found:
        warning = f"\n\n⚠️ Note: This response mentions {', '.join(found)} (or a closely related variation), which you were advised earlier to avoid. Please double-check this against your injury, limitation, or intolerance before proceeding, or consult a professional."
        answer = answer + warning

    return answer

def extract_avoided_items(conversation_history, coach_type):
    if not conversation_history:
        return None

    item_type = COACH_ITEM_TYPE.get(coach_type, "exercise")
    history_text = "\n".join(
        [f"User: {t['question']}\nCoach: {t['answer']}" for t in conversation_history]
    )
    extraction_prompt = f"""Read the following coaching conversation. List ONLY the specific {item_type} names that the coach said to avoid, are unsafe, or should not be done or consumed, due to injury, limitation, allergy, or intolerance. Respond with a short comma-separated list of names only (e.g., "Overhead Press, Lateral Raises"). If none were mentioned as something to avoid, respond with exactly: None

Conversation:
{history_text}

Items to avoid:"""

    result = generate_response(extraction_prompt)
    return result.strip()

def extract_plan_structure(answer_text, coach_type):
    extraction_prompt = f"""Read the following coaching response. If it contains a multi-day plan (workout days or meal days), extract it into strict JSON with this exact shape, and respond with ONLY the JSON, no other text, no markdown formatting, no code fences:
{{"days": [{{"label": "Day 1", "items": ["item one", "item two"]}}]}}

Each item should be a short single line (e.g., "Barbell Bench Press: 3 sets of 8-12 reps" or "Grilled chicken breast with quinoa"). If the response does not contain a clear multi-day plan, respond with exactly: NONE

Coaching response:
{answer_text}

JSON:"""

    result = generate_response(extraction_prompt)
    result = result.strip()

    if result.upper() == "NONE":
        return None

    if result.startswith("```"):
        result = result.strip("`")
        if result.lower().startswith("json"):
            result = result[4:]
        result = result.strip()

    start = result.find("{")
    end = result.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None

    json_text = result[start:end + 1]

    try:
        import json
        parsed = json.loads(json_text)
        if "days" in parsed and isinstance(parsed["days"], list):
            return parsed
    except Exception:
        return None

    return None

def extract_injury_context(conversation_history):
    if not conversation_history:
        return None

    history_text = "\n".join(
        [f"User: {t['question']}\nCoach: {t['answer']}" for t in conversation_history]
    )
    extraction_prompt = f"""Read the following coaching conversation. Identify if the user mentioned an injury or physical limitation tied to a specific body part or joint. Respond with exactly ONE of these words and nothing else: knee, shoulder, lower back, hip, wrist, ankle, none

Conversation:
{history_text}

Body part:"""

    result = generate_response(extraction_prompt).strip().lower()
    for key in INJURY_RISK_EXERCISES:
        if key in result:
            return key
    return None

def merge_avoided_with_injury_risk(avoided_items, injury_key):
    risk_list = INJURY_RISK_EXERCISES.get(injury_key, [])
    existing = []
    if avoided_items and avoided_items.lower() != "none":
        existing = [e.strip() for e in avoided_items.split(",") if e.strip()]

    combined = existing[:]
    existing_lower = [e.lower() for e in existing]
    for risk_item in risk_list:
        if risk_item.lower() not in existing_lower:
            combined.append(risk_item.title())

    return ", ".join(combined) if combined else None

def get_rag_response(user_question, coach_type="bodybuilding", k=3, profile=None, conversation_history=None):
    chunks = retrieve_relevant_chunks(user_question, k=k, coach_type=coach_type)

    avoided_items = extract_avoided_items(conversation_history, coach_type)

    if coach_type in ("bodybuilding", "powerlifting", "fatloss"):
        injury_key = extract_injury_context(conversation_history)
        if injury_key:
            avoided_items = merge_avoided_with_injury_risk(avoided_items, injury_key)

    prompt = build_prompt(user_question, chunks, coach_type=coach_type, profile=profile, conversation_history=conversation_history, avoided_items=avoided_items)
    answer = generate_response(prompt)
    answer = check_for_avoided_items(answer, avoided_items, coach_type)
    return answer, chunks


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