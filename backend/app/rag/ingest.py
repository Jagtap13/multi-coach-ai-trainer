import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Path to the folder containing our knowledge base .txt files
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
VECTOR_STORE_DIR = os.path.join(os.path.dirname(__file__), "vector_store")

def load_and_chunk_documents():
    loader = DirectoryLoader(
        KNOWLEDGE_BASE_DIR,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    # Tag each document with its coach type, derived from filename
    for doc in documents:
        filename = os.path.basename(doc.metadata.get("source", ""))
        coach_type = filename.replace(".txt", "")
        doc.metadata["coach_type"] = coach_type

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    return chunks

def build_vector_store(chunks):
    print("Loading embedding model (this may take a moment on first run)...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("Building FAISS index from chunks...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    vector_store.save_local(VECTOR_STORE_DIR)
    print(f"FAISS index saved to {VECTOR_STORE_DIR}")

    return vector_store

def test_retrieval(vector_store, query, k=3):
    print(f"\n--- Test query: '{query}' ---")
    results = vector_store.similarity_search(query, k=k)
    for i, doc in enumerate(results, 1):
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        print(f"\n[{i}] From: {source}")
        print(doc.page_content[:200] + "...")

if __name__ == "__main__":
    chunks = load_and_chunk_documents()
    print("\n--- Sample chunk ---")
    print(chunks[0].page_content)
    print("\nSource:", chunks[0].metadata)

    print("\n--- Building vector store ---")
    vector_store = build_vector_store(chunks)

    test_retrieval(vector_store, "What rep range is best for muscle growth?")
    test_retrieval(vector_store, "How much protein should I eat to lose fat?")