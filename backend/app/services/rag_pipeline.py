import sys
import os

# Allow imports from sibling folders (rag/, llm/)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm"))

from retriever import retrieve_relevant_chunks
from ollama_client import generate_response

def build_prompt(user_question, retrieved_chunks):
    context = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])

    prompt = f"""You are a knowledgeable fitness coach. Use the following trusted fitness information to answer the user's question accurately. If the information doesn't fully answer the question, use your general knowledge but stay consistent with the provided context.

Context:
{context}

Question: {user_question}

Answer:"""
    return prompt

def get_rag_response(user_question, k=3):
    chunks = retrieve_relevant_chunks(user_question, k=k)
    prompt = build_prompt(user_question, chunks)
    answer = generate_response(prompt)
    return answer, chunks

if __name__ == "__main__":
    question = "What rep range should I use to build muscle?"
    print(f"Question: {question}\n")

    answer, sources = get_rag_response(question)

    print("--- Answer ---")
    print(answer)

    print("\n--- Sources used ---")
    for chunk in sources:
        source = os.path.basename(chunk.metadata.get("source", "unknown"))
        print(f"- {source}")