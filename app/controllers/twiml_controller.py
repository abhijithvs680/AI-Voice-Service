"""TwiML controller - Twilio webhook for call connection."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.services.twilio_service import TwilioService

router = APIRouter(tags=["twiml"])
twilio_service = TwilioService()


@router.post("/twiml")
async def serve_twiml(request: Request) -> HTMLResponse:
    """Return TwiML for Twilio to connect the call to our WebSocket."""
    persona_id = request.query_params.get("persona_id", "")
    if not persona_id:
        persona_id = "vet_care_assistant"

    form_data = await request.form()
    to_number = form_data.get("To", "")
    from_number = form_data.get("From", "")

    twiml = twilio_service.generate_twiml(persona_id, to_number, from_number)
    return HTMLResponse(content=twiml, media_type="application/xml")
