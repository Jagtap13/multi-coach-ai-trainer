import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from database import get_db
from auth_dependency import get_current_user
from workout_plan import WorkoutPlan
from rag_pipeline import extract_plan_structure
from plan_pdf import build_plan_pdf

router = APIRouter()

class SavePlanRequest(BaseModel):
    coach_type: str
    title: str
    raw_text: str

class PlanResponse(BaseModel):
    id: int
    coach_type: str
    title: str
    raw_text: str
    plan_data: str | None
    created_at: str

    class Config:
        from_attributes = True

@router.post("/plans")
def save_plan(request: SavePlanRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    structured = extract_plan_structure(request.raw_text, request.coach_type)
    plan_data_json = json.dumps(structured) if structured else None

    new_plan = WorkoutPlan(
        user_id=current_user.id,
        coach_type=request.coach_type,
        title=request.title,
        raw_text=request.raw_text,
        plan_data=plan_data_json,
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return {
        "id": new_plan.id,
        "coach_type": new_plan.coach_type,
        "title": new_plan.title,
        "raw_text": new_plan.raw_text,
        "plan_data": json.loads(new_plan.plan_data) if new_plan.plan_data else None,
        "created_at": new_plan.created_at.isoformat(),
    }

@router.get("/plans")
def list_plans(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    plans = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id
    ).order_by(WorkoutPlan.created_at.desc()).all()

    return [
        {
            "id": p.id,
            "coach_type": p.coach_type,
            "title": p.title,
            "raw_text": p.raw_text,
            "plan_data": json.loads(p.plan_data) if p.plan_data else None,
            "created_at": p.created_at.isoformat(),
        }
        for p in plans
    ]

@router.get("/plans/{plan_id}/pdf")
def download_plan_pdf(plan_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Same ownership check as delete: a user can only export their own plans.
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    try:
        plan_data = json.loads(plan.plan_data) if plan.plan_data else None
    except json.JSONDecodeError:
        # Malformed structured data - fall back to the raw text layout.
        plan_data = None

    pdf_bytes = build_plan_pdf(
        title=plan.title,
        coach_type=plan.coach_type,
        created_at=plan.created_at,
        plan_data=plan_data,
        raw_text=plan.raw_text,
    )

    # ASCII-only filename in the header (titles can contain any characters);
    # the frontend sets the friendly filename itself when saving the blob.
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="plan-{plan.id}.pdf"'},
    )

@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"deleted": True}