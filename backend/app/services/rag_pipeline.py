import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "coaches"))

from retriever import retrieve_relevant_chunks
from ollama_client import generate_response
from coach_prompts import get_coach_prompt

def build_prompt(user_question, retrieved_chunks, coach_type):
    context = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])
    coach_persona = get_coach_prompt(coach_type)

    prompt = f"""{coach_persona}

Use the following trusted fitness information to answer the user's question accurately. If the information doesn't fully answer the question, use your general knowledge but stay consistent with the provided context and your coaching persona.

Context:
{context}

Question: {user_question}

Answer:"""
    return prompt

def get_rag_response(user_question, coach_type="bodybuilding", k=3):
    chunks = retrieve_relevant_chunks(user_question, k=k)
    prompt = build_prompt(user_question, chunks, coach_type)
    answer = generate_response(prompt)
    return answer, chunks

if __name__ == "__main__":
    question = "What rep range should I use to build muscle?"

    for coach in ["bodybuilding", "powerlifting"]:
        print(f"\n{'='*50}")
        print(f"Coach: {coach.upper()}")
        print(f"Question: {question}\n")

        answer, sources = get_rag_response(question, coach_type=coach)

        print("--- Answer ---")
        print(answer)