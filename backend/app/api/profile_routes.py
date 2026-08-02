import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from auth_dependency import get_current_user
from user import User

router = APIRouter(prefix="/profile", tags=["profile"])

class ProfileUpdate(BaseModel):
    age: int | None = None
    weight_kg: float | None = None
    experience_level: str | None = None
    goal: str | None = None

class ProfileResponse(BaseModel):
    age: int | None
    weight_kg: float | None
    experience_level: str | None
    goal: str | None

    class Config:
        from_attributes = True

@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("", response_model=ProfileResponse)
def update_profile(
    updates: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if updates.age is not None:
        current_user.age = updates.age
    if updates.weight_kg is not None:
        current_user.weight_kg = updates.weight_kg
    if updates.experience_level is not None:
        current_user.experience_level = updates.experience_level
    if updates.goal is not None:
        current_user.goal = updates.goal

    db.commit()
    db.refresh(current_user)
    return current_user