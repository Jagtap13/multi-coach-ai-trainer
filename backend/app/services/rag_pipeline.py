import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "coaches"))

from retriever import retrieve_relevant_chunks
from ollama_client import generate_response
from coach_prompts import get_coach_prompt

def build_prompt(user_question, retrieved_chunks, coach_type, profile=None):
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

        if details:
            profile_section = f"\nUser profile:\n{chr(10).join(details)}\n\nTailor your answer specifically to this user's profile above — consider their experience level and goal when giving advice.\n"

    prompt = f"""{coach_persona}
    {profile_section}

Use the following trusted fitness information to answer the user's question accurately. If the information doesn't fully answer the question, use your general knowledge but stay consistent with the provided context and your coaching persona.

Context:
{context}

Question: {user_question}

Answer:"""
    return prompt

def get_rag_response(user_question, coach_type="bodybuilding", k=3,profile=None):
    chunks = retrieve_relevant_chunks(user_question, k=k)
    prompt = build_prompt(user_question, chunks, coach_type,profile=profile)
    answer = generate_response(prompt)
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
    question = "What rep range should I use to build muscle?"
    sample_profile={
        "age":22,
        "weight_kg":65,
        "experience_level":"beginner",
        "goal":"build muscle"
    }
    answer, sources = get_rag_response(question,coach_type="bodybuilding",profile=sample_profile)
    print("--- Answer (with profile) ---")
    print(answer)