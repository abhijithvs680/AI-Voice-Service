"""WebSocket controller - Twilio Media Streams."""

import traceback

from fastapi import APIRouter, WebSocket
from loguru import logger
from pipecat.runner.types import WebSocketRunnerArguments

from app.services.bot_service import run_bot

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle WebSocket connection from Twilio Media Streams."""
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    try:
        runner_args = WebSocketRunnerArguments(websocket=websocket)
        await run_bot(runner_args)
    except Exception as e:
        logger.error(f"WebSocket error: {e}\n{traceback.format_exc()}")
        try:
            await websocket.close()
        except Exception as close_err:
            logger.debug(f"WebSocket close error: {close_err}")
