# Multi-Coach AI Personal Trainer Simulator

An AI-powered fitness coaching platform featuring four specialized coach personalities — Bodybuilding, Powerlifting, Nutrition, and Fat Loss — each grounded in a Retrieval-Augmented Generation (RAG) pipeline over curated fitness knowledge, with personalized advice based on user profile data.

> AI-generated fitness guidance — not a substitute for professional medical advice.

## Features

- **Four specialized AI coaches**, each with a distinct personality and a dedicated knowledge base
- **Coach-scoped RAG retrieval** — each coach only searches its own knowledge base, preventing cross-contamination between domains
- **Personalized recommendations** based on user profile (age, weight, gender, experience level, goal)
- **Session-based chat threading** — ChatGPT-style conversation history, grouped by session, with per-conversation delete
- **Secure authentication** — JWT-based login/register with hashed passwords
- **Safety-hardened prompts** — tested against prompt injection, hallucinated advice, contradictory numeric guidance, and off-topic requests
- **Voice input** *(Beta)* — hands-free question input via the Web Speech API
- **Conversation export** — download any chat thread as a `.txt` file
- **Responsive UI** — usable on both desktop and mobile

## Tech Stack

**Backend**
- FastAPI (Python)
- LangChain + FAISS (vector search)
- Sentence-Transformers (`all-MiniLM-L6-v2`, CPU-forced for compatibility)
- Ollama running Llama 3 (local LLM inference)
- PostgreSQL (Neon, serverless)
- SQLAlchemy ORM
- JWT authentication (`python-jose`, `passlib`/`bcrypt`)

**Frontend**
- React + Vite
- Tailwind CSS v4

## Architecture Overview

- User Question → Coach-Scoped Retriever (FAISS) → Relevant Knowledge Chunks
- → Coach Personality Prompt + Safety Clause + User Profile
- → Llama 3 (via Ollama) → Response → Saved to Chat History (PostgreSQL)


Each coach's knowledge base is embedded and tagged with `coach_type` metadata at ingestion time, so retrieval is filtered per-coach — the Bodybuilding coach only ever searches bodybuilding content, and so on.

## Project Structure

ai-trainer-simulator/
├── backend/
│ └── app/
│ ├── main.py # FastAPI app, chat + conversation endpoints
│ ├── rag/ # Knowledge base, ingestion, retrieval
│ ├── coaches/ # Coach personality prompts + safety rules
│ ├── services/ # RAG pipeline (prompt building + LLM calls)
│ ├── llm/ # Ollama client
│ ├── models/ # SQLAlchemy models (User, ChatHistory)
│ ├── api/ # Auth + profile routes
│ └── core/ # Database, security, auth dependency
└── frontend/
└── src/
├── App.jsx # Main layout, coach selection, profile
├── ChatWindow.jsx # Chat UI, session threading, voice input
├── HistoryPanel.jsx # Conversation history list
├── ProfileForm.jsx # User profile form
└── AuthForm.jsx # Login / register


## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed locally, with `llama3` pulled (`ollama pull llama3`)
- A PostgreSQL database (e.g., a free [Neon](https://neon.tech) instance)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```
Create a `.env` file with your database URL and JWT secret (see `core/database.py` and `core/security.py` for expected variable names).

Ingest the knowledge base to build the FAISS index:
```bash
cd app/rag
python ingest.py
```

Run the server:
```bash
cd ../..
cd app
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

## Known Limitations

- **Voice input (Beta)**: uses the browser's native Web Speech API, which streams audio to the browser vendor's speech recognition service. Reliability varies significantly by browser — verified working via Windows' native dictation, but transcription can fail in Brave (network-blocked by privacy shields) and inconsistently in Edge. This is a browser/platform limitation, not an application bug.
- **No multi-turn memory within a single answer**: each response is generated independently based on retrieved context and profile, without carrying forward earlier turns in the same conversation into the prompt.
- **GPU-independent by design**: embeddings are forced to run on CPU for compatibility across machines with limited VRAM (developed on an RTX 3050, 4GB VRAM).

## Safety Approach

Every coach prompt is appended with a shared safety clause covering: medical/injury disclaimers, minor safety, avoidance of extreme diet advice, avoidance of invented brand names, scope boundaries (redirecting off-topic requests), and role-lock protections against prompt injection. These were tested iteratively with before/after evidence during development.

## Team

- Karan Bhope
- Aditya Jagtap
- Akshay Wankhede

Guided by Prof. Madhuri Ramsetti — G H Raisoni College of Engineering and Management, Pune (SPPU)

