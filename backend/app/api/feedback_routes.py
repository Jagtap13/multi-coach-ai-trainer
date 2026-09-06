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

ADMIN_EMAILS = {"test@example.com"}

def require_admin(current_user):
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")

class FeedbackRequest(BaseModel):
    chat_history_id: int
    rating: str
    reason: str | None = None

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
        existing.reason = request.reason
        db.commit()
        return {"id": existing.id, "rating": existing.rating, "reason": existing.reason}

    new_feedback = MessageFeedback(
        user_id=current_user.id,
        chat_history_id=request.chat_history_id,
        rating=request.rating,
        reason=request.reason,
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return {"id": new_feedback.id, "rating": new_feedback.rating, "reason": new_feedback.reason}

@router.get("/feedback/summary")
def feedback_summary(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
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

@router.get("/feedback/downvoted")
def get_downvoted(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    results = db.query(
        MessageFeedback.id,
        MessageFeedback.reason,
        MessageFeedback.created_at,
        ChatHistory.coach_type,
        ChatHistory.question,
        ChatHistory.answer
    ).join(
        ChatHistory, MessageFeedback.chat_history_id == ChatHistory.id
    ).filter(
        MessageFeedback.user_id == current_user.id,
        MessageFeedback.rating == "down"
    ).order_by(MessageFeedback.created_at.desc()).all()

    return [
        {
            "id": r.id,
            "reason": r.reason,
            "created_at": r.created_at.isoformat(),
            "coach_type": r.coach_type,
            "question": r.question,
            "answer": r.answer,
        }
        for r in results
    ]

@router.get("/auth/is-admin")
def check_is_admin(current_user=Depends(get_current_user)):
    return {"is_admin": current_user.email in ADMIN_EMAILS}