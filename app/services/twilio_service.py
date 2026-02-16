"""Twilio service - initiate calls and generate TwiML."""

import re

from loguru import logger
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import Connect, Stream, VoiceResponse

from app.config import get_domain, get_twilio_config, get_websocket_url
from app.models.persona import get_persona


PHONE_E164_PATTERN = re.compile(r"^\+?[0-9]{10,15}$")


def validate_phone(phone_number: str) -> bool:
    """Validate phone number (E.164-like)."""
    return bool(PHONE_E164_PATTERN.match(phone_number.replace(" ", "")))


class TwilioService:
    """Service for Twilio voice operations."""

    def __init__(self) -> None:
        self._client: TwilioClient | None = None

    def _get_client(self) -> TwilioClient:
        if self._client is None:
            sid, token, _ = get_twilio_config()
            if not sid or not token:
                raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN required")
            self._client = TwilioClient(sid, token)
        return self._client

    def initiate_call(self, to_number: str, persona_id: str) -> dict:
        """Initiate outbound call. Returns {call_sid, status, to_number}."""
        if get_persona(persona_id) is None:
            raise ValueError(f"Unknown persona: {persona_id}")

        if not validate_phone(to_number):
            raise ValueError("Invalid phone number. Use E.164 format (e.g. +1234567890)")

        sid, token, from_number = get_twilio_config()
        if not all([sid, token, from_number]):
            raise ValueError("Twilio credentials or phone number missing")

        domain = get_domain()
        twiml_url = f"{domain}/twiml?persona_id={persona_id}"

        try:
            client = self._get_client()
            call = client.calls.create(
                to=to_number,
                from_=from_number,
                url=twiml_url,
                method="POST",
            )
            return {
                "call_sid": call.sid,
                "status": "call_initiated",
                "to_number": to_number,
            }
        except Exception as e:
            logger.error(f"Twilio call failed: {e}")
            raise

    def generate_twiml(self, persona_id: str, to_number: str, from_number: str) -> str:
        """Generate TwiML for Twilio Stream connection."""
        websocket_url = get_websocket_url()
        response = VoiceResponse()
        connect = Connect()
        stream = Stream(url=websocket_url)
        stream.parameter(name="persona_id", value=persona_id)
        stream.parameter(name="to_number", value=to_number)
        stream.parameter(name="from_number", value=from_number)
        connect.append(stream)
        response.append(connect)
        return str(response)
