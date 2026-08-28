import sys
import os
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth_dependency import get_current_user
from progress import ProgressEntry

router = APIRouter()

class ProgressEntryCreate(BaseModel):
    weight_kg: float
    entry_date: date
    notes: str | None = None

class ProgressEntryResponse(BaseModel):
    id: int
    weight_kg: float
    entry_date: date
    notes: str | None

    class Config:
        from_attributes = True

@router.post("/progress", response_model=ProgressEntryResponse)
def create_progress_entry(entry: ProgressEntryCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    new_entry = ProgressEntry(
        user_id=current_user.id,
        weight_kg=entry.weight_kg,
        entry_date=entry.entry_date,
        notes=entry.notes,
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@router.get("/progress", response_model=list[ProgressEntryResponse])
def list_progress_entries(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    entries = db.query(ProgressEntry).filter(
        ProgressEntry.user_id == current_user.id
    ).order_by(ProgressEntry.entry_date.asc()).all()
    return entries

@router.delete("/progress/{entry_id}")
def delete_progress_entry(entry_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(ProgressEntry).filter(
        ProgressEntry.id == entry_id,
        ProgressEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Progress entry not found")
    db.delete(entry)
    db.commit()
    return {"deleted": True}