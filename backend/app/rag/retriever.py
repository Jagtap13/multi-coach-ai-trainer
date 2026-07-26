import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_STORE_DIR = os.path.join(os.path.dirname(__file__), "vector_store")

def load_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(
        VECTOR_STORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_store

def retrieve_relevant_chunks(query, k=3):
    vector_store = load_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return results

if __name__ == "__main__":
    test_query = "What's a good workout split for building muscle?"
    chunks = retrieve_relevant_chunks(test_query)
    for i, chunk in enumerate(chunks, 1):
        source = os.path.basename(chunk.metadata.get("source", "unknown"))
        print(f"[{i}] From: {source}")
        print(chunk.page_content[:200])
        print()