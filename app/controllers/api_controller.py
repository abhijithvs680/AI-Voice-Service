"""API controller - personas and call initiation."""

from fastapi import APIRouter, HTTPException, Request

from app.models.persona import load_personas
from app.services.twilio_service import TwilioService

api_router = APIRouter(prefix="/api", tags=["api"])
call_router = APIRouter(tags=["call"])
twilio_service = TwilioService()


@api_router.get("/personas")
async def list_personas() -> dict:
    """Return personas from persona.json."""
    data = load_personas()
    return {"personas": data.get("personas", [])}


@call_router.post("/call")
async def initiate_call(request: Request) -> dict:
    """Initiate an outbound Twilio call."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    persona_id = body.get("persona_id")
    phone_number = body.get("phone_number")

    if not persona_id or not phone_number:
        raise HTTPException(
            status_code=400,
            detail="persona_id and phone_number are required",
        )

    try:
        result = twilio_service.initiate_call(phone_number, persona_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
