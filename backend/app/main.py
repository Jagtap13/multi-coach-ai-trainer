import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "llm"))
sys.path.append(os.path.join(os.path.dirname(__file__), "coaches"))
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))
sys.path.append(os.path.join(os.path.dirname(__file__), "api"))
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "models"))

from fastapi import FastAPI, HTTPException, Depends 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth_routes import router as auth_router
from rag_pipeline import get_rag_response
from coach_prompts import COACH_PROMPTS
from auth_dependency import get_current_user
from profile_routes import router as profile_router
from database import get_db
from chat_history import ChatHistory

app = FastAPI(title="AI Personal Trainer Simulator API")
app.include_router(auth_router)
app.include_router(profile_router)

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserProfile(BaseModel):
    age: int | None = None
    weight_kg: float | None = None
    experience_level: str | None = None  # beginner, intermediate, advanced
    goal: str | None = None

class ChatRequest(BaseModel):
    question: str
    coach_type: str = "bodybuilding"
    profile: UserProfile | None = None

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
def chat(request: ChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if request.coach_type.lower() not in COACH_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid coach_type. Choose from: {list(COACH_PROMPTS.keys())}"
        )

    try:
        answer, chunks = get_rag_response(
            request.question,
            coach_type=request.coach_type,
            profile=request.profile.model_dump() if request.profile else None
        )
        sources = list(set(os.path.basename(c.metadata.get("source", "unknown")) for c in chunks))

        # Save to chat history
        history_entry = ChatHistory(
            user_id=current_user.id,
            coach_type=request.coach_type,
            question=request.question,
            answer=answer,
            sources=",".join(sources)
        )
        db.add(history_entry)
        db.commit()

        return ChatResponse(
            answer=answer,
            coach_type=request.coach_type,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history")
def get_chat_history(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).all()

    return [
        {
            "id": r.id,
            "coach_type": r.coach_type,
            "question": r.question,
            "answer": r.answer,
            "sources": r.sources.split(",") if r.sources else [],
            "created_at": r.created_at.isoformat()
        }
        for r in records
    ]