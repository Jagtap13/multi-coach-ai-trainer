import re
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
    "squat": ["squat", "squats", "back squat", "front squat"],
    "deadlift": ["deadlift", "deadlifts", "conventional deadlift", "sumo deadlift"],
    "running": ["running", "jogging", "sprinting", "treadmill running"],
}

FOOD_SYNONYMS = {
    "dairy": ["dairy", "milk", "cheese", "yogurt", "cream"],
    "peanuts": ["peanuts", "peanut butter", "peanut"],
    "gluten": ["gluten", "wheat", "bread", "pasta", "flour"],
    "shellfish": ["shellfish", "shrimp", "prawns", "crab", "lobster"],
    "eggs": ["eggs", "egg", "egg whites"],
    "soy": ["soy", "soybean", "tofu", "soy sauce"],
}

def get_synonym_map(coach_type):
    return FOOD_SYNONYMS if coach_type == "nutrition" else EXERCISE_SYNONYMS

SAFE_CONTEXT_MARKERS = [
    "avoid", "without", "free", "non-dairy", "dairy-free", "gluten-free",
    "allerg", "intoleran", "instead of", "substitute", "alternative",
    "not include", "excluding", "rather than",
]

SAFE_QUALIFIER_PHRASES = {
    "milk": ["almond milk", "coconut milk", "soy milk", "oat milk", "rice milk", "cashew milk", "pea milk", "hemp milk"],
    "yogurt": ["coconut yogurt", "soy yogurt", "almond yogurt", "cashew yogurt"],
    "cheese": ["cashew cheese", "almond cheese", "vegan cheese", "dairy-free cheese"],
}

def sentence_has_real_match(sentence_lower, alias):
    cleaned = sentence_lower
    for phrase in SAFE_QUALIFIER_PHRASES.get(alias, []):
        cleaned = cleaned.replace(phrase, "")
    return alias in cleaned

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
    sentences = re.split(r'(?<=[.!?])\s+', answer)
    found = []

    for item in item_list:
        aliases = expand_with_synonyms(item, coach_type)
        item_found = False
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for alias in aliases:
                if alias in sentence_lower and sentence_has_real_match(sentence_lower, alias):
                    has_safe_context = any(marker in sentence_lower for marker in SAFE_CONTEXT_MARKERS)
                    if not has_safe_context:
                        item_found = True
                        break
            if item_found:
                break
        if item_found:
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


def get_rag_response(user_question, coach_type="bodybuilding", k=3, profile=None, conversation_history=None):
    chunks = retrieve_relevant_chunks(user_question, k=k, coach_type=coach_type)

    avoided_items = extract_avoided_items(conversation_history, coach_type)

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