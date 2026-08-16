import sys
import os
import uuid

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
    gender: str | None = None

class ChatRequest(BaseModel):
    question: str
    coach_type: str = "bodybuilding"
    profile: UserProfile | None = None
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    answer: str
    coach_type: str
    sources: list[str]
    conversation_id: str

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
        conv_id = request.conversation_id or str(uuid.uuid4())
        # Save to chat history
        history_entry = ChatHistory(
            user_id=current_user.id,
            conversation_id=conv_id,
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
            sources=sources,
            conversation_id=conv_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.delete("/chat/history")
def clear_chat_history(
    coach_type: str | None = None,
    conversation_id: str | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)
    if coach_type:
        query = query.filter(ChatHistory.coach_type == coach_type)
    if conversation_id:
        query = query.filter(ChatHistory.conversation_id == conversation_id)
    deleted_count = query.delete()
    db.commit()
    return {"deleted": deleted_count}

@app.get("/chat/conversations")
def list_conversations(coach_type: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id,
        ChatHistory.coach_type == coach_type
    ).order_by(ChatHistory.created_at.asc()).all()

    conversations = {}
    for r in records:
        if r.conversation_id not in conversations:
            conversations[r.conversation_id] = {
                "conversation_id": r.conversation_id,
                "title": r.question[:60],
                "created_at": r.created_at.isoformat(),
                "message_count": 0,
            }
        conversations[r.conversation_id]["message_count"] += 1

    result = list(conversations.values())
    result.sort(key=lambda c: c["created_at"], reverse=True)
    return result

@app.get("/chat/conversations/{conversation_id}")
def get_conversation_messages(conversation_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id,
        ChatHistory.conversation_id == conversation_id
    ).order_by(ChatHistory.created_at.asc()).all()

    if not records:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return [
        {
            "id": r.id,
            "question": r.question,
            "answer": r.answer,
            "sources": r.sources.split(",") if r.sources else [],
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]