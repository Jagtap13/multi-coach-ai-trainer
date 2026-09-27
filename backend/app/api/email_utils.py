"""
Email utility for sending password reset links via Gmail SMTP.

Setup required before this works:
1. Use a Gmail account with 2-Step Verification enabled.
2. Generate an App Password: Google Account -> Security -> 2-Step
   Verification -> App Passwords. Choose "Mail" as the app.
   This gives you a 16-character password - use that, NOT your real
   Gmail password.
3. Set these two environment variables before starting the backend:
       GMAIL_ADDRESS=youraccount@gmail.com
       GMAIL_APP_PASSWORD=your16charapppassword
   Easiest way: create a .env file in the backend root and load it
   with python-dotenv (pip install python-dotenv --break-system-packages),
   or set them directly in PowerShell for the session:
       $env:GMAIL_ADDRESS="youraccount@gmail.com"
       $env:GMAIL_APP_PASSWORD="your16charapppassword"
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


def send_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Sends a password reset email with a link back to the frontend.
    Returns True if the email was sent successfully, False otherwise
    (caller decides whether to surface this or fail silently).
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("[email] GMAIL_ADDRESS / GMAIL_APP_PASSWORD not set - cannot send email.")
        print(f"[email] For local testing, here is the reset link instead: "
              f"{FRONTEND_URL}/?reset_token={reset_token}")
        return False

    reset_link = f"{FRONTEND_URL}/?reset_token={reset_token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset your AI Personal Trainer password"
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_email

    text_body = (
        "You requested a password reset for your AI Personal Trainer account.\n\n"
        f"Click this link to reset your password: {reset_link}\n\n"
        "This link expires in 30 minutes. If you didn't request this, "
        "you can safely ignore this email."
    )

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1C1D1F;">
        <h2>Reset your password</h2>
        <p>You requested a password reset for your AI Personal Trainer account.</p>
        <p>
          <a href="{reset_link}"
             style="display:inline-block; padding:10px 20px; background:#C0503D;
                    color:#fff; text-decoration:none; border-radius:6px;">
            Reset Password
          </a>
        </p>
        <p style="color:#888; font-size:13px;">
          This link expires in 30 minutes. If you didn't request this,
          you can safely ignore this email.
        </p>
      </body>
    </html>
    """

    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, message.as_string())
        return True
    except Exception as e:
        print(f"[email] Failed to send reset email: {e}")
        return False