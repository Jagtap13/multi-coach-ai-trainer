import sys
import os
import secrets
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from database import get_db
from user import User
from security import hash_password, verify_password, create_access_token
from email_utils import send_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])

RESET_TOKEN_EXPIRE_MINUTES = 30

# Set this to the OAuth Client ID from Google Cloud Console
# (Credentials -> OAuth 2.0 Client IDs -> Web application).
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class GoogleAuthRequest(BaseModel):
    # The signed ID token handed back by Google Identity Services on
    # the frontend after the user picks their Google account.
    credential: str

@router.post("/register", response_model=TokenResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    # Always return the same generic message, whether or not the email
    # exists - this avoids leaking which emails are registered.
    generic_message = "If an account with that email exists, a reset link has been sent."

    if not user:
        return ForgotPasswordResponse(message=generic_message)

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    db.commit()

    sent = send_reset_email(request.email, token)
    if not sent:
        # Email sending failed (e.g. credentials not configured yet).
        # The token is still valid in the DB and gets logged to the
        # console by send_reset_email for local testing, but we don't
        # leak that failure detail to the client.
        print(f"[auth] Email delivery failed for {request.email}, but reset token was created.")

    return ForgotPasswordResponse(message=generic_message)

@router.post("/reset-password", response_model=TokenResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == request.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if user.reset_token_expires is None or user.reset_token_expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user.hashed_password = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    # Log the user in immediately after a successful reset, same as
    # register/login, so they don't have to log in twice.
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)

@router.post("/google", response_model=TokenResponse)
def google_login(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google sign-in is not configured on the server (GOOGLE_CLIENT_ID not set)."
        )

    try:
        # Verifies the token's signature and audience against Google's
        # public keys - raises ValueError if the token is invalid,
        # expired, or wasn't issued for this app.
        payload = google_id_token.verify_oauth2_token(
            request.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google credential")

    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        # First time signing in with this Google account - create a
        # local user record. There's no real password for a
        # Google-only account, so we set an unusable random one; the
        # existing forgot-password flow still works if they later want
        # to set a real password and log in normally too.
        random_password = secrets.token_urlsafe(24)
        user = User(
            email=email,
            hashed_password=hash_password(random_password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)