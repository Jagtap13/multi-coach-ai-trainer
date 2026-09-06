import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth_dependency import get_current_user
from feedback import MessageFeedback
from chat_history import ChatHistory

router = APIRouter()

class FeedbackRequest(BaseModel):
    chat_history_id: int
    rating: str

@router.post("/feedback")
def submit_feedback(request: FeedbackRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if request.rating not in ("up", "down"):
        raise HTTPException(status_code=400, detail="Rating must be 'up' or 'down'")

    message = db.query(ChatHistory).filter(
        ChatHistory.id == request.chat_history_id,
        ChatHistory.user_id == current_user.id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    existing = db.query(MessageFeedback).filter(
        MessageFeedback.user_id == current_user.id,
        MessageFeedback.chat_history_id == request.chat_history_id
    ).first()

    if existing:
        existing.rating = request.rating
        db.commit()
        return {"id": existing.id, "rating": existing.rating}

    new_feedback = MessageFeedback(
        user_id=current_user.id,
        chat_history_id=request.chat_history_id,
        rating=request.rating,
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return {"id": new_feedback.id, "rating": new_feedback.rating}

@router.get("/feedback/summary")
def feedback_summary(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    results = db.query(
        ChatHistory.coach_type,
        MessageFeedback.rating
    ).join(
        MessageFeedback, MessageFeedback.chat_history_id == ChatHistory.id
    ).filter(
        MessageFeedback.user_id == current_user.id
    ).all()

    summary = {}
    for coach_type, rating in results:
        if coach_type not in summary:
            summary[coach_type] = {"up": 0, "down": 0}
        summary[coach_type][rating] += 1

    return summary