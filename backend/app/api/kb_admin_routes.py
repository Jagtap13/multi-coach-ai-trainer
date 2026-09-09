import sys
import os
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth_dependency import get_current_user

router = APIRouter()

ADMIN_EMAILS = {"test@example.com"}

def require_admin(current_user):
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")

KB_DIR = os.path.join(os.path.dirname(__file__), "..", "rag", "knowledge_base")
RAG_DIR = os.path.join(os.path.dirname(__file__), "..", "rag")

ALLOWED_FILES = {"bodybuilding.txt", "powerlifting.txt", "nutrition.txt", "fatloss.txt"}

class KBUpdateRequest(BaseModel):
    content: str

@router.get("/admin/knowledge-base")
def list_knowledge_base(current_user=Depends(get_current_user)):
    require_admin(current_user)

    files = {}
    for filename in sorted(ALLOWED_FILES):
        path = os.path.join(KB_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                files[filename] = f.read()
        else:
            files[filename] = ""
    return files

@router.put("/admin/knowledge-base/{filename}")
def update_knowledge_base(filename: str, request: KBUpdateRequest, current_user=Depends(get_current_user)):
    require_admin(current_user)

    if filename not in ALLOWED_FILES:
        raise HTTPException(status_code=400, detail="Invalid knowledge base file")

    path = os.path.join(KB_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(request.content)

    try:
        result = subprocess.run(
            ["python", "ingest.py"],
            cwd=RAG_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Re-ingestion failed: {result.stderr[-500:]}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Re-ingestion timed out")

    return {"saved": True, "reingested": True}