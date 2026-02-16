"""FastAPI application - wires MVC components."""

from fastapi import FastAPI

from app.controllers.api_controller import api_router, call_router
from app.controllers.twiml_controller import router as twiml_router
from app.controllers.web_controller import router as web_router
from app.controllers.websocket_controller import router as websocket_router

app = FastAPI(title="AI Voice Service")

app.include_router(web_router)
app.include_router(api_router)
app.include_router(call_router)
app.include_router(twiml_router)
app.include_router(websocket_router)
