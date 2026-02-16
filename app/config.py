"""Application configuration from environment."""

import os

from dotenv import load_dotenv

load_dotenv(override=True)


def get_domain() -> str:
    """Get DOMAIN from env, stripped of trailing slash."""
    domain = os.getenv("DOMAIN", "").rstrip("/")
    if not domain:
        raise ValueError(
            "DOMAIN environment variable is required (e.g. https://xxx.ngrok-free.app)"
        )
    return domain


def get_websocket_url() -> str:
    """Get wss:// URL for Twilio Stream."""
    domain = get_domain()
    ws_url = domain.replace("https://", "wss://").replace("http://", "wss://")
    return f"{ws_url}/ws"


def get_api_key() -> str:
    """Get Google/Gemini API key."""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY must be set")
    return key


def get_twilio_config() -> tuple[str, str, str]:
    """Get (account_sid, auth_token, from_number)."""
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    phone = os.getenv("TWILIO_PHONE_NUMBER")
    return sid or "", token or "", phone or ""
