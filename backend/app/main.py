import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "coaches"))
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_pipeline import get_rag_response
from coach_prompts import COACH_PROMPTS

app = FastAPI(title="AI Personal Trainer Simulator API")

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    coach_type: str = "bodybuilding"

class ChatResponse(BaseModel):
    answer: str
    coach_type: str
    sources: list[str]

@app.get("/")
def root():
    return {"message": "AI Personal Trainer Simulator API is running"}

@app.get("/coaches")
def list_coaches():
    return {"available_coaches": list(COACH_PROMPTS.keys())}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if request.coach_type.lower() not in COACH_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid coach_type. Choose from: {list(COACH_PROMPTS.keys())}"
        )

    try:
        answer, chunks = get_rag_response(request.question, coach_type=request.coach_type)
        sources = list(set(os.path.basename(c.metadata.get("source", "unknown")) for c in chunks))

        return ChatResponse(
            answer=answer,
            coach_type=request.coach_type,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))